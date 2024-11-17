from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet, ListStyle
from reportlab.platypus import (
    Paragraph,
    Spacer,
    Frame,
    PageTemplate,
    BaseDocTemplate,
    NextPageTemplate,
    PageBreak,
    Preformatted,
    ListFlowable,
    ListItem,
)
from reportlab.lib.units import inch


class TwoColumnTemplate(BaseDocTemplate):
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        page_width, page_height = letter

        # First page frames (with title area)
        first_page_col1 = Frame(
            inch / 2,
            inch,
            (page_width - 1.5 * inch) / 2,
            page_height - 0.40 * inch,
            id="first_col1",
        )
        first_page_col2 = Frame(
            (page_width + 0.5 * inch) / 2,
            inch,
            (page_width - 1.5 * inch) / 2,
            page_height - 4 * inch,
            id="first_col2",
        )

        # Content frames for two-column pages
        content_col1 = Frame(inch / 2, inch, (page_width - 1.5 * inch) / 2, page_height - 2 * inch, id="col1")
        content_col2 = Frame(
            (page_width + 0.5 * inch) / 2, inch, (page_width - 1.5 * inch) / 2, page_height - 2 * inch, id="col2"
        )

        # Single column frame for appendix
        appendix_frame = Frame(inch, inch, page_width - 2 * inch, page_height - 2 * inch, id="appendix")

        def first_page(canvas, doc):
            canvas.saveState()
            canvas.setFont("Times-Bold", 20)
            canvas.drawCentredString(page_width / 2, page_height - 1.5 * inch, "Tool Pre-Selection Using Embeddings")
            canvas.setFont("Times-Roman", 14)
            canvas.drawCentredString(page_width / 2, page_height - 2.25 * inch, "André Baltazar")
            canvas.setFont("Times-Roman", 11)
            canvas.drawCentredString(page_width / 2, page_height - 2.45 * inch, "me@andrebaltazar.com")
            canvas.restoreState()

        # Create page templates
        self.addPageTemplates(
            [
                PageTemplate(id="FirstPage", frames=[first_page_col1, first_page_col2], onPage=first_page),
                PageTemplate(id="ContentPage", frames=[content_col1, content_col2]),
                PageTemplate(id="AppendixPage", frames=[appendix_frame]),
            ]
        )


def main():
    # Paper content structure
    sections = {
        "Abstract": (
            "As the ecosystem of tools and agents available for integration with Large Language Models "
            "(LLMs) expands, selecting the most relevant tools for a given task becomes critical for "
            "efficiency and improving interaction quality. This paper explores the use of vector-based search and embeddings "
            "to pre-select tools from a large pool (e.g., 100+ tools), ensuring a more targeted and "
            "contextually relevant interaction. Additionally, this approach can be extended to agent "
            "orchestration systems, such as OpenAI's Swarm [1], to optimize handoffs between agents in complex multi-agent scenarios."
        ),
        "1. Introduction": (
            "Modern LLMs are increasingly being augmented with external tools to extend their capabilities, "
            "such as retrieving real-time information, performing complex calculations, or manipulating structured "
            "data. While maintaining a large pool of tools does not inherently create computational overhead, passing "
            "an excessive number of tools into the LLM can lead to context length constraints and inefficiencies. "
            "Efficiently narrowing down the pool of tools to those most relevant to a user's query is crucial to ensure "
            "seamless interaction and reduce token usage.\n\n"
            "Vector-based search, leveraging embeddings to represent tools and user queries in a shared high-dimensional "
            "space, provides a scalable and efficient mechanism for this pre-selection. Techniques such as Hypothetical "
            "Document Embeddings (HyDE) [2] can further enhance the matching process by generating hypothetical intermediate "
            "outputs to better align queries with tool capabilities.\n\n"
            "In addition, systems like OpenAI's Swarm, which orchestrate the actions of multiple specialized agents, face "
            "similar challenges of scalability and relevance. Embedding-based approaches can be extended to optimize agent "
            "selection in these multi-agent environments."
        ),
        "2. Methodology": {
            "content": "",
            "subsections": {
                "2.1 Tool Embedding Generation": (
                    "Each tool is described using its metadata, documentation, and sample use cases. These descriptions are converted "
                    "into embeddings using transformer-based models (e.g., OpenAI embeddings or Sentence-BERT). The tool representation "
                    "may vary, but the core idea is to capture the tool's functionality, parameters, and potential use cases in a way that is "
                    "easy to understand, and create a relevant embedding. The embedding process could include:"
                ),
                "2.1_list": [
                    "Metadata Representation: Capturing the tool's core functionality, parameters, and potential use cases",
                    "Contextual Examples: Generating short synthetic examples of tool usage to enrich the embedding",
                ],
                "2.2 Query Embedding and HyDE": (
                    "When a user provides a query, it is embedded into the same vector space as the tools. Optionally, the Hypothetical "
                    "Document Embeddings (HyDE) technique generates a plausible response to the query and embeds this response. The final "
                    "query embedding can then be a blend of the direct query embedding and the HyDE-enhanced embedding, improving alignment "
                    "with tool capabilities."
                ),
                "2.3 Vector-Based Matching": (
                    "The cosine similarity between the query embedding and each tool embedding is computed. Tools are ranked based on "
                    "similarity scores, and the top results are selected. These tools can either be directly passed to the LLM or used "
                    "as input for further decision-making processes."
                ),
                "2.4 Extension to Agent-Orchestration Systems": (
                    "In multi-agent systems like OpenAI's Swarm, each agent's capabilities and domain expertise can be embedded using a "
                    "similar methodology. Tasks or queries are matched to the most relevant agents, enabling efficient decomposition and "
                    "assignment in complex scenarios."
                ),
            },
        },
        "3. Applications": {
            "content": "",
            "subsections": {
                "3.1 Pre-Selection of Tools for LLMs": (
                    "The described approach allows systems to pre-select a subset of tools to pass into the LLM, ensuring that only the "
                    "most relevant options occupy the limited context space. This prevents wasting tokens on irrelevant tools and allows "
                    "the LLM to focus on producing high-quality results."
                ),
                "3.2 Agent Selection in Multi-Agent Frameworks": (
                    "Embedding-based filtering is also used to dynamically assign tasks to the best-suited agents in systems like OpenAI's "
                    "Swarm. This approach can further optimize multi-agent systems by ensuring that each agent is utilized according to its "
                    "strengths and capabilities."
                ),
            },
        },
        "4. Implementation": {
            "content": (
                "A practical implementation of the vector-based search approach has been developed and tested. "
                "The system successfully demonstrates the effectiveness of embedding-based tool selection in reducing context size and "
                "improving response relevance.\n\n"
                "The implementation uses modern embedding models to generate high-quality vector representations of both tools and queries. "
                "Detailed pseudocode for the implementation is provided in Appendix A, which covers the core components including "
                "tool embedding generation, query processing with optional HyDE enhancement, and similarity-based ranking."
            )
        },
        "5. Experiments": {
            "content": (
                "An experiment was conducted to evaluate the effectiveness of the vector-based tool selection approach. "
                "The system was tested with a configurable number of tools (default 100) and test queries (default 400). "
                "These tools and queries were generated by AI, and minimal processing was done to curate them.\n\n"
                "Each experiment followed these steps:"
            ),
            "steps_list": [
                "Tool Embedding: All tools were embedded into vector space using the Nomic Embed Text model.",
                "Query Processing: Each query was passed through an HyDE pass to generate a generate an hypotetical description "
                "of the tool that would be used to answer the query.",
                "Vector-Based Matching: The cosine similarity between the HyDE-enhanced query embedding and each tool embedding was computed "
                "and the top 5 tools were selected based on cosine similarity.",
                "Metrics collected: Token usage (measuring the number of tokens required to represent the selected tools versus the full tool set) and selection accuracy (determining whether the expected tool was included in the vector-selected subset).",
            ],
            "subsections": {
                "5.1 Results": (
                    "The pre-selection obviously results in a very high reduction in terms of token usage, because reducing from 100 "
                    "to 5 tools would reduce the token usage by 95% for most queries if we consider the tools to have around the same size in tokens. "
                    "The interesting part is attempting to maintain a high selection accuracy while reducing the token usage, which makes it possible to run "
                    "in smaller models.\n\n"
                    "The results show that the vector-based approach is able to maintain a high selection accuracy even when the number of tools is increased. "
                    "In the majority of the test runs, the expected tool was in the top 5 results. This accounts for more than 94% of the test queries. "
                    "Using HyDE, the selection accuracy was able to reach higher accuracy, sometimes more than 98%, for runs of 400 queries, especially when the queries were trickier.\n\n"
                    "For example, if the query was \"Hash the contents: 'How's the weather today?'\", the expected tool would be "
                    "a hashing tool, instead of a weather tool. These are the cases where the HyDE technique is better than just using the "
                    "plain query embedding.\n\n"
                    "The results were obtained by running over multiple runs of 400 queries with 100 tools. The code for the experiment, "
                    "with one example test run, is available at https://github.com/AndreBaltazar8/tool-pre-selection.\n\n"
                ),
                "5.2 Discussion": (
                    "The experimental results were obtained using a limited dataset of AI-generated tools and queries, which introduces "
                    "potential sampling bias as these may not fully represent real-world use cases. Nevertheless, the findings demonstrate "
                    "that the vector-based approach successfully maintains high selection accuracy as the toolset scales, while achieving "
                    "substantial reductions in token utilization.\n\n"
                    "The integration of HyDE in the query embedding pipeline introduces additional "
                    "computational overhead but yields improved selection accuracy. With appropriate prompt engineering, the technique "
                    "demonstrates robust performance even when using smaller models.\n\n"
                    "Smaller models like 3B parameters still result in a good selection accuracy, which makes it possible to run HyDE "
                    "at an higher token/s and increase the selection accuracy.\n\n"
                    "Further research opportunities include evaluating the approach using a more comprehensive, manually curated dataset "
                    "of tools and queries. Additionally, empirical validation through end-to-end testing with LLM-based tool execution "
                    "would provide valuable insights into the practical impact of reducing the tool context from 100 to 5 options. It could also "
                    "be interesting to normalize the description of the tools in regards to what the HyDE generates, which would increase the "
                    "selection accuracy even more."
                ),
            },
        },
        "6. Conclusion": (
            "Vector-based search and embedding techniques provide an efficient mechanism for narrowing down large pools of tools or "
            "agents in LLM-driven systems. By leveraging techniques like HyDE and embedding-based similarity, these systems dynamically "
            "identify the most relevant tools or agents for a given task.\n\n"
            "This approach has been successfully implemented in real-world systems to pre-select tools that are passed into the LLM or, "
            "in some cases, to outright select the best tool for the task."
        ),
        "Acknowledgments": (
            "I want to express my deep gratitude to my good friend, José Camacho, for our insightful discussions on these topics. "
            "He pointed me to the HyDE technique and suggested it as an approach for achieving more relevant "
            "results when selecting tools, compared to relying solely on embeddings of the input query."
        ),
        "References": (
            "1. OpenAI Cookbook, 'Orchestrating Agents with Swarm', https://cookbook.openai.com/examples/orchestrating_agents\n\n"
            "2. Gao et al., 'Precise Zero-Shot Dense Retrieval without Relevance Labels', arXiv:2212.10496, https://doi.org/10.48550/arXiv.2212.10496\n\n"
        ),
        "Disclaimer": (
            "This paper was co-written by AI with additional guidance from the human editor. "
            "The pseudocode in Appendix A was fully written with AI assistance."
        ),
    }

    # Appendix structure
    appendices = {
        "A": {
            "title": "Implementation",
            "content": (
                "Below is a high-level pseudocode representation of how vector-based search can be used to select relevant tools:\n\n"
                "# Step 1: Embed all tools into a shared vector space\n"
                "def generate_tool_embeddings(tool_descriptions, embedding_model):\n"
                "    tool_embeddings = {}\n"
                "    for tool_name, description in tool_descriptions.items():\n"
                "        embedding = embedding_model.encode(description)\n"
                "        tool_embeddings[tool_name] = embedding\n"
                "    return tool_embeddings\n"
                "\n"
                "# Step 2: Embed the user query and (optionally) use HyDE\n"
                "def generate_query_embedding(query, embedding_model, use_hyde=False):\n"
                "    if use_hyde:\n"
                "        hypothetical_response = generate_hypothetical_response(query)\n"
                "        query_embedding = embedding_model.encode(hypothetical_response)\n"
                "    else:\n"
                "        query_embedding = embedding_model.encode(query)\n"
                "    return query_embedding\n"
                "\n"
                "# Step 3: Calculate cosine similarity between query and tools\n"
                "def rank_tools(query_embedding, tool_embeddings):\n"
                "    similarities = {}\n"
                "    for tool_name, tool_embedding in tool_embeddings.items():\n"
                "        similarity = cosine_similarity(query_embedding, tool_embedding)\n"
                "        similarities[tool_name] = similarity\n"
                "    return sorted(similarities.items(), key=lambda x: x[1], reverse=True)\n"
                "\n"
                "# Step 4: Select top-N tools to pass to the LLM\n"
                "def select_relevant_tools(query, tool_descriptions, embedding_model, top_n=5, use_hyde=False):\n"
                "    tool_embeddings = generate_tool_embeddings(tool_descriptions, embedding_model)\n"
                "    query_embedding = generate_query_embedding(query, embedding_model, use_hyde)\n"
                "    ranked_tools = rank_tools(query_embedding, tool_embeddings)\n"
                "    return [tool for tool, score in ranked_tools[:top_n]]\n"
                "\n"
                "# Example usage\n"
                "tool_descriptions = {\n"
                "    'WeatherAPI': 'Provides real-time weather data for a given location.',\n"
                "    'Calculator': 'Performs basic and advanced mathematical calculations.',\n"
                "    'Translator': 'Translates text between multiple languages.',\n"
                "    # Add more tools...\n"
                "}\n"
                "\n"
                'query = "What\'s the weather in New York?"\n'
                "embedding_model = SomeEmbeddingModel()  # Use your embedding model here\n"
                "selected_tools = select_relevant_tools(\n"
                "    query,\n"
                "    tool_descriptions,\n"
                "    embedding_model,\n"
                "    top_n=3,\n"
                "    use_hyde=True\n"
                ")\n"
                "\n"
                "print('Selected tools:', selected_tools)"
            ),
            "footer": (
                "This pseudocode demonstrates how tools can be pre-selected based on their embeddings and the similarity to a query. "
                "Similar logic applies to agent selection, with agent descriptions replacing tool descriptions."
            ),
        }
    }

    doc = TwoColumnTemplate("tool-pre-selection-using-embeddings.pdf", pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom styles
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading1"],
        fontSize=12,
        spaceAfter=4,
        spaceBefore=12,
        bold=True,
        alignment=0,  # Left alignment for numbered sections
    )

    # Special style for Abstract heading (centered)
    abstract_heading_style = ParagraphStyle(
        "AbstractHeading",
        parent=styles["Heading1"],
        fontSize=12,
        spaceAfter=4,
        spaceBefore=12,
        bold=True,
        alignment=1,  # Centered alignment for Abstract
    )

    subheading_style = ParagraphStyle(
        "CustomSubHeading",
        parent=styles["Heading2"],
        fontSize=11,
        spaceAfter=4,
        spaceBefore=0,
        leftIndent=0,  # Removed left indent
        bold=True,
        alignment=0,  # Left alignment for subsections
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=4,
        leading=14,
        alignment=4,  # Justified text
    )

    # Custom styles for code
    code_style = ParagraphStyle(
        "CustomCode",
        parent=styles["Code"],
        fontSize=8,
        fontName="Courier",
        leading=9,  # Reduced leading for tighter code
        alignment=0,
        leftIndent=20,
        firstLineIndent=0,
        spaceBefore=6,
        spaceAfter=6,
    )

    # Add bullet list style
    bullet_list_style = ListStyle(
        "BulletList",
        leftIndent=10,
        rightIndent=0,
        bulletAlign="right",
        bulletType="bullet",
        bulletColor=colors.black,
        bulletFontName="Helvetica",
        bulletFontSize=10,
        bulletDedent=4,
        spaceBefore=0,
        spaceAfter=10,
    )

    # Add numbered list style
    numbered_list_style = ListStyle(
        "NumberedList",
        leftIndent=20,
        rightIndent=0,
        bulletAlign="right",
        bulletFormat="%s.",
        bulletType="1",
        bulletFontName="Helvetica",
        bulletFontSize=10,
        bulletDedent=15,
        spaceBefore=0,
        spaceAfter=10,
    )

    # Content elements
    elements = []

    # Add spacing after title for first page
    elements.append(Spacer(1, 3.5 * inch))

    # Add sections
    for section_title, content in sections.items():
        if section_title == "1. Introduction":
            elements.append(NextPageTemplate("ContentPage"))

        if section_title == "Abstract":
            elements.append(Paragraph(section_title, abstract_heading_style))
        else:
            elements.append(Paragraph(section_title, heading_style))

        if isinstance(content, dict):
            if content.get("content"):
                paragraphs = content["content"].split("\n\n")
                for para in paragraphs:
                    elements.append(Paragraph(para, body_style))

            # Add the steps list if present
            if content.get("steps_list"):
                bullet_list = []
                for item in content["steps_list"]:
                    bullet_list.append(ListItem(Paragraph(item, body_style)))
                elements.append(ListFlowable(bullet_list, bulletType="1", style=numbered_list_style))

            if content.get("subsections"):
                for subsection_title, subsection_content in content["subsections"].items():
                    if not subsection_title.endswith("_list"):
                        elements.append(Paragraph(subsection_title, subheading_style))
                        if isinstance(subsection_content, str):
                            paragraphs = subsection_content.split("\n\n")
                            for para in paragraphs:
                                elements.append(Paragraph(para, body_style))
                    if subsection_title == "2.1_list":
                        bullet_list = []
                        for item in subsection_content:
                            bullet_list.append(ListItem(Paragraph(item, body_style)))
                        elements.append(ListFlowable(bullet_list, bulletType="bullet", style=bullet_list_style))

            if content.get("footer"):
                elements.append(Paragraph(content["footer"], body_style))

        else:
            paragraphs = content.split("\n\n")
            for para in paragraphs:
                elements.append(Paragraph(para, body_style))

    # Add appendices
    for appendix_id, appendix in appendices.items():
        elements.append(NextPageTemplate("AppendixPage"))
        elements.append(PageBreak())
        elements.append(Paragraph(f"Appendix {appendix_id}: {appendix['title']}", heading_style))

        # Add introduction text
        intro, code = appendix["content"].split("\n\n", 1)
        elements.append(Paragraph(intro, body_style))

        # Add code block using Preformatted
        elements.append(Spacer(1, 12))
        elements.append(Preformatted(code, code_style))
        elements.append(Spacer(1, 12))

        # Add footer if present
        if appendix.get("footer"):
            elements.append(Paragraph(appendix["footer"], body_style))

    # Build the document
    doc.build(elements)


if __name__ == "__main__":
    main()
