import ollama from "ollama";
import { cosinesim } from "./utils";
import fs from "fs/promises";
import path from "path";

interface Tool {
  name: string;
  description: string;
  category: string;
  embedding?: number[];
}

interface ExperimentResult {
  query: string;
  vectorSelectedTools: string[];
  vectorResponseTime: number;
  vectorTokenCount: number;
  fullToolsResponseTime: number;
  fullToolsTokenCount: number;
  expectedTool: string;
  correct: boolean;
}

const model = "qwen2.5-coder:32b";
const embeddingModel = "nomic-embed-text";

interface CachedData {
  tools: Tool[];
  testQueries?: TestQuery[];
}

interface TestQuery {
  query: string;
  expectedTool: string;
}

interface Config {
  toolCount: number;
  queryCount: number;
  useHyDE: boolean;
}

export class ToolSelector {
  private tools: Tool[] = [];
  private readonly toolsPath = path.join(__dirname, "tools.json");
  private initialized: Promise<void>;
  private readonly queriesPath = path.join(__dirname, "test-queries.json");
  private config: Config;

  private readonly TEST_GENERATION_PROMPT = `Given these tools, generate a natural user query that would require a tool to answer.
The query should be realistic and specific, as if asked by a user.
Focus on the actual task the user wants to accomplish, not the tools themselves.

Example format:
- "What's the current temperature in Paris?"
- "Can you translate this document from Spanish to English?"
- "Schedule a meeting with the team for next Tuesday at 2 PM"`;

  constructor(config?: Partial<Config>) {
    this.config = {
      toolCount: config?.toolCount ?? 100,
      queryCount: config?.queryCount ?? 400,
      useHyDE: config?.useHyDE ?? true,
    };
    this.initialized = this.init();
  }

  private async init(): Promise<void> {
    this.tools = await this.loadTools();
  }

  private async loadTools(): Promise<Tool[]> {
    try {
      const toolsData = await fs.readFile(this.toolsPath, "utf-8");
      const allCachedTools = JSON.parse(toolsData).tools;

      if (allCachedTools.length > this.config.toolCount) {
        console.log(
          `Found ${allCachedTools.length} cached tools, using random ${this.config.toolCount} for this session...`
        );
        return allCachedTools
          .sort(() => Math.random() - 0.5)
          .slice(0, this.config.toolCount);
      } else if (allCachedTools.length < this.config.toolCount) {
        console.log(
          `Found ${allCachedTools.length} cached tools, generating ${
            this.config.toolCount - allCachedTools.length
          } more...`
        );
        const categories = [
          "weather",
          "math",
          "translation",
          "search",
          "calendar",
          "email",
          "file",
          "database",
          "api",
          "system",
        ];

        for (let i = allCachedTools.length; i < this.config.toolCount; i++) {
          const category = categories[i % categories.length];
          let isUnique = false;
          let tool: Tool;
          let attempts = 0;
          const maxAttempts = 10;

          while (!isUnique && attempts < maxAttempts) {
            attempts++;
            const description = await this.generateToolDescription(category, i);

            // Get embedding for new description
            const response = await ollama.embeddings({
              model: embeddingModel,
              prompt: description,
            });
            const newEmbedding = response.embedding;

            // Check similarity with existing tools
            let tooSimilar = false;
            for (const existingTool of allCachedTools) {
              if (existingTool.embedding) {
                const similarity = cosinesim(
                  newEmbedding,
                  existingTool.embedding
                );
                if (similarity > 0.9) {
                  console.log(
                    `Description too similar (${similarity.toFixed(
                      3
                    )}) to existing tool: ${existingTool.name}`
                  );
                  tooSimilar = true;
                  break;
                }
              }
            }

            if (tooSimilar) continue;

            const name = await this.generateToolName(description);

            // Check if name already exists
            if (allCachedTools.some((t: Tool) => t.name === name)) {
              console.log(`Tool name "${name}" already exists, retrying...`);
              continue;
            }

            tool = {
              name,
              description,
              category,
              embedding: newEmbedding,
            };
            isUnique = true;
          }

          if (!isUnique) {
            throw new Error(
              `Failed to generate unique tool after ${maxAttempts} attempts`
            );
          }

          allCachedTools.push(tool!);

          console.log(
            `Generated tool ${i + 1}/${this.config.toolCount}: ${tool!.name}`
          );
          console.log(`Description: ${tool!.description}`);
        }

        await this.cacheTools(allCachedTools);
      }

      return allCachedTools;
    } catch (error) {
      const tools = await this.generateTestTools();
      await this.cacheTools(tools);
      return tools;
    }
  }

  private async cacheTools(tools: Tool[]): Promise<void> {
    const dataToCache: CachedData = { tools };
    await fs.writeFile(this.toolsPath, JSON.stringify(dataToCache, null, 2));
  }

  async embedTools(): Promise<void> {
    await this.ensureInitialized();
    // Only generate embeddings if they don't exist
    const toolsNeedingEmbeddings = this.tools.filter((tool) => !tool.embedding);

    for (const tool of toolsNeedingEmbeddings) {
      const response = await ollama.embeddings({
        model: embeddingModel,
        prompt: tool.description,
      });
      tool.embedding = response.embedding;
    }

    if (toolsNeedingEmbeddings.length > 0) {
      await this.cacheTools(this.tools);
    }
  }

  private async ensureInitialized(): Promise<void> {
    await this.initialized;
  }

  private async generateToolDescription(
    category: string,
    index: number
  ): Promise<string> {
    const prompt = `Generate a brief, specific description (1-2 sentences) for a tool in the '${category}' category. The tool should be practical and focused on a single, specific ${category}-related task. Make it sound professional and implementation-neutral. It should solve one clear problem, avoiding broad or multi-purpose functionality. For example, instead of a general file converter, it should specifically convert PDFs to Word documents. Instead of a general communication tool, it should specifically send emails. Make it imperative like a description or a command, not a general brief.`;

    const response = await ollama.chat({
      model,
      messages: [
        {
          role: "system",
          content:
            "You are a technical writer creating clear, concise tool descriptions.",
        },
        {
          role: "user",
          content: prompt,
        },
      ],
      stream: false,
    });

    return response.message.content.trim();
  }

  private async generateToolName(description: string): Promise<string> {
    const response = await ollama.chat({
      model,
      messages: [
        {
          role: "system",
          content:
            "Generate a brief, descriptive CamelCase name (3-6 words combined) for a tool based on its description. The name should reflect the tool's main functionality, with precise, specific words that specify the tool's purpose. Make it imperative like a command, not a noun.",
        },
        {
          role: "user",
          content: `Tool description: ${description}\nGenerate only the CamelCase name, nothing else.`,
        },
      ],
      stream: false,
    });

    const name = response.message.content
      .trim()
      .replace(/[^a-zA-Z]/g, "") // Remove any non-letter characters
      .replace(/^[a-z]/, (c) => c.toUpperCase()); // Ensure first character is uppercase

    return name;
  }

  private async generateTestTools(): Promise<Tool[]> {
    try {
      const cachedTools = await fs.readFile(this.toolsPath, "utf-8");
      return JSON.parse(cachedTools);
    } catch (error) {
      const categories = [
        "weather",
        "math",
        "translation",
        "search",
        "calendar",
        "email",
        "file",
        "database",
        "api",
        "system",
      ];
      const tools: Tool[] = [];

      for (let i = 0; i < this.config.toolCount; i++) {
        const category = categories[i % categories.length];
        let isUnique = false;
        let tool: Tool;
        let attempts = 0;
        const maxAttempts = 10;

        while (!isUnique && attempts < maxAttempts) {
          attempts++;
          const description = await this.generateToolDescription(category, i);

          // Get embedding for new description
          const response = await ollama.embeddings({
            model: embeddingModel,
            prompt: description,
          });
          const newEmbedding = response.embedding;

          // Check similarity with existing tools
          let tooSimilar = false;
          for (const existingTool of tools) {
            if (existingTool.embedding) {
              const similarity = cosinesim(
                newEmbedding,
                existingTool.embedding
              );
              if (similarity > 0.98) {
                console.log(
                  `Description too similar (${similarity.toFixed(
                    3
                  )}) to existing tool: ${existingTool.name}`
                );
                tooSimilar = true;
                break;
              }
            }
          }

          if (tooSimilar) continue;

          const name = await this.generateToolName(description);

          // Check if name already exists
          if (tools.some((t) => t.name === name)) {
            console.log(`Tool name "${name}" already exists, retrying...`);
            continue;
          }

          tool = {
            name,
            description,
            category,
            embedding: newEmbedding,
          };
          isUnique = true;
        }

        if (!isUnique) {
          throw new Error(
            `Failed to generate unique tool after ${maxAttempts} attempts`
          );
        }

        tools.push(tool!);

        console.log(
          `Generated tool ${i + 1}/${this.config.toolCount}: ${tool!.name}`
        );
        console.log(`Description: ${tool!.description}`);
      }

      await this.cacheTools(tools);
      return tools;
    }
  }

  private async generateHyDE(query: string): Promise<string> {
    const response = await ollama.chat({
      model,
      messages: [
        {
          role: "system",
          content:
            "You are a technical writer creating clear, concise tool descriptions.",
        },
        {
          role: "user",
          content: `Based on the user's request, generate a brief, focused description of a tool that would handle this request.
Use these examples as a guide:

Example requests and their tool descriptions:
1. Request: 'Send an email to John'
   Description: Sends emails to specified recipients with customizable content

2. Request: 'Convert 5 meters to feet'
   Description: Converts values between different measurement units

3. Request: 'Set a reminder for tomorrow at 2pm'
   Description: Creates time-based reminders with custom messages

4. Request: 'Generate a random password'
   Description: Generates secure random passwords with configurable options

5. Request: 'Compress this image'
   Description: Compresses images while preserving quality

Request: ${query}
Description:`,
        },
      ],
      stream: false,
    });

    return response.message.content;
  }

  async selectTools(
    query: string,
    useHyDE: boolean = false,
    topK: number = 5
  ): Promise<string[]> {
    await this.ensureInitialized();
    const queryText = useHyDE ? await this.generateHyDE(query) : query;
    const response = await ollama.embeddings({
      model: embeddingModel,
      prompt: queryText,
    });
    const queryEmbedding = response.embedding;

    const similarities = this.tools.map((tool) => ({
      name: tool.name,
      similarity: tool.embedding
        ? cosinesim(queryEmbedding, tool.embedding)
        : 0,
    }));

    return similarities
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, topK)
      .map((t) => t.name);
  }

  async runExperiment(queries: TestQuery[]): Promise<ExperimentResult[]> {
    await this.ensureInitialized();
    await this.embedTools();
    const results: ExperimentResult[] = [];
    let totalCorrect = 0;

    for (let i = 0; i < queries.length; i++) {
      const query = queries[i].query;
      const expectedTool = queries[i].expectedTool;

      const startVector = Date.now();
      const vectorSelectedTools = await this.selectTools(
        query,
        this.config.useHyDE
      );
      const vectorResponseTime = Date.now() - startVector;

      const startFull = Date.now();
      const allToolNames = this.tools.map((t) => t.name);
      const fullToolsResponseTime = Date.now() - startFull;

      const vectorTokenCount = vectorSelectedTools.reduce(
        (acc, tool) => acc + tool.length + this.getToolDescription(tool).length,
        0
      );
      const fullToolsTokenCount = allToolNames.reduce(
        (acc, tool) => acc + tool.length + this.getToolDescription(tool).length,
        0
      );

      const correct = vectorSelectedTools.includes(expectedTool);
      totalCorrect += correct ? 1 : 0;
      const runningAccuracy = (totalCorrect / (i + 1)) * 100;

      console.log(`\nQuery ${i + 1}: "${query}"`);
      console.log(`Expected Tool: ${expectedTool}`);
      console.log(`Selected Tools: ${vectorSelectedTools.join(", ")}`);
      console.log(
        correct ? "✓ Correct Tool Selected" : "✗ Incorrect Tool Selected"
      );
      console.log(
        `Running Accuracy: ${runningAccuracy.toFixed(1)}% (${totalCorrect}/${
          i + 1
        })`
      );

      results.push({
        query,
        vectorSelectedTools,
        vectorResponseTime,
        vectorTokenCount,
        fullToolsResponseTime,
        fullToolsTokenCount,
        expectedTool,
        correct,
      });
    }

    return results;
  }

  private getToolDescription(toolName: string): string {
    return this.tools.find((t) => t.name === toolName)?.description || "";
  }

  private async generateTestQuery(availableTools: Tool[]): Promise<TestQuery> {
    const toolDescriptions = availableTools
      .map((tool) => `Tool: ${tool.name}\nDescription: ${tool.description}\n`)
      .join("\n");

    const response = await ollama.chat({
      model,
      messages: [
        {
          role: "system",
          content:
            "Call the provided tool to generate a realistic user query that would require one of the specified tools. Call the function with the query and expected tool name, nothing else.",
        },
        {
          role: "user",
          content: `${this.TEST_GENERATION_PROMPT}\n\nAvailable Tools:\n${toolDescriptions}`,
        },
      ],
      stream: false,
      tools: [
        {
          type: "function",
          function: {
            name: "generate_query",
            description:
              "Generate a realistic user query that would require one of the specified tools.",
            parameters: {
              type: "object",
              required: ["query", "tool"],
              properties: {
                query: { type: "string", description: "The query to generate" },
                tool: { type: "string", description: "The tool to use" },
              },
            },
          },
        },
      ],
    });

    const calls = response.message.tool_calls;
    if (calls?.length !== 1) {
      throw new Error("Expected exactly one tool call");
    }

    const call = calls[0];
    const query = call.function.arguments.query;
    const expectedTool = call.function.arguments.tool;

    return {
      query,
      expectedTool,
    };
  }

  private async loadTestQueries(): Promise<TestQuery[]> {
    try {
      const data = await fs.readFile(this.queriesPath, "utf-8");
      return JSON.parse(data).testQueries;
    } catch (error) {
      return [];
    }
  }

  private async cacheTestQueries(queries: TestQuery[]): Promise<void> {
    await fs.writeFile(
      this.queriesPath,
      JSON.stringify({ testQueries: queries }, null, 2)
    );
  }

  async generateTestQueries(): Promise<TestQuery[]> {
    await this.ensureInitialized();

    const allCachedQueries = await this.loadTestQueries();

    if (allCachedQueries.length > this.config.queryCount) {
      console.log(
        `Found ${allCachedQueries.length} cached queries, using random ${this.config.queryCount} for this session...`
      );
      return allCachedQueries
        .sort(() => Math.random() - 0.5)
        .slice(0, this.config.queryCount);
    }

    const remainingCount = this.config.queryCount - allCachedQueries.length;

    if (remainingCount <= 0) {
      console.log("Using cached test queries");
      return allCachedQueries;
    }

    console.log(
      `Found ${allCachedQueries.length} cached queries, generating ${remainingCount} more...`
    );
    const newQueries: TestQuery[] = [];

    for (let i = 0; i < remainingCount; i++) {
      let attempt = 0;
      const maxAttempts = 10;
      while (attempt < maxAttempts) {
        try {
          const randomTools = [...this.tools]
            .sort(() => Math.random() - 0.5)
            .slice(0, 5);
          const testQuery = await this.generateTestQuery(randomTools);
          newQueries.push(testQuery);

          console.log(
            `Generated test query ${allCachedQueries.length + i + 1}/${
              this.config.queryCount
            }:`
          );
          console.log(`Query: ${testQuery.query}`);
          console.log(`Expected Tool: ${testQuery.expectedTool}\n`);
          break;
        } catch (error) {
          attempt++;
          if (attempt === maxAttempts) {
            throw error;
          }
          console.log(`Attempt ${attempt} failed, retrying...`);
        }
      }
    }

    const allQueries = [...allCachedQueries, ...newQueries];
    await this.cacheTestQueries(allQueries);
    return allQueries.slice(0, this.config.queryCount);
  }
}

function parseArgs(): Partial<Config> {
  const config: Partial<Config> = {};
  const args = process.argv.slice(2);

  for (const arg of args) {
    const [key, value] = arg.split("=");
    if (key === "--tools") {
      config.toolCount = parseInt(value);
    } else if (key === "--queries") {
      config.queryCount = parseInt(value);
    } else if (key === "--hyde") {
      config.useHyDE = value.toLowerCase() !== "false";
    }
  }

  return config;
}

async function runExperiments() {
  const config = parseArgs();
  const selector = new ToolSelector(config);
  await selector.embedTools();

  console.log("\nGenerating Test Queries...");
  const testQueries = await selector.generateTestQueries();

  console.log("\nRunning Experiments...");
  const results = await selector.runExperiment(testQueries);

  console.log("\nSummary Statistics:");
  console.log("==================");

  const totalCorrect = results.filter((r) => r.correct).length;
  const totalVectorTime = results.reduce(
    (acc, r) => acc + r.vectorResponseTime,
    0
  );
  const totalFullTime = results.reduce(
    (acc, r) => acc + r.fullToolsResponseTime,
    0
  );
  const totalVectorTokens = results.reduce(
    (acc, r) => acc + r.vectorTokenCount,
    0
  );
  const totalFullTokens = results.reduce(
    (acc, r) => acc + r.fullToolsTokenCount,
    0
  );

  console.log(
    `Average Vector Search Time: ${(totalVectorTime / results.length).toFixed(
      2
    )}ms`
  );
  console.log(
    `Average Full Tools Time: ${(totalFullTime / results.length).toFixed(2)}ms`
  );
  console.log(
    `Average Vector Tokens: ${(totalVectorTokens / results.length).toFixed(2)}`
  );
  console.log(
    `Average Full Tools Tokens: ${(totalFullTokens / results.length).toFixed(
      2
    )}`
  );
  console.log(
    `Token Reduction: ${(
      (1 - totalVectorTokens / totalFullTokens) *
      100
    ).toFixed(1)}%`
  );
  console.log(
    `Final Tool Selection Accuracy: ${(
      (totalCorrect / results.length) *
      100
    ).toFixed(1)}% (${totalCorrect}/${results.length})`
  );
  console.log(`Total Queries: ${results.length}`);
}

// Handle the async nature of the code
if (require.main === module) {
  runExperiments().catch(console.error);
}
