"""
Prompt templates for the OpenBridge server.
These prompts guide the AI assistant in understanding and interacting
with the PAD system.
"""

from typing import List, Dict, Any, Optional
from fastmcp.prompts.base import UserMessage, AssistantMessage


def pad_system_introduction() -> str:
    """
    Main system introduction prompt that provides comprehensive context about the PAD system.
    """
    return """
You are assisting researchers working with the PAD (Paper-based Analytical Device) system. This system uses reagent-based cards to analyze chemical samples, particularly for drug testing and identification.

AVAILABLE CONTEXT:
- An ontology defining the semantic relationships between PAD components is available via the download_ontology tool
- Card images can be analyzed with the compute_average_rgb tool for specific regions of interest
- API endpoints return JSON-LD data mapped to the PAD ontology for semantic understanding

ENTITY RELATIONSHIPS:
- AnalyticalCard: The physical card with reagent lanes that captures samples reacting with reagents
- Layout: Defines geometric arrangement of lanes, bounding boxes, and fiducials
- Project: Organizational grouping of multiple cards with defined test parameters
- ColorBarcode: Result pattern produced by chemical reactions used for analysis
- Sample: Drug or substance being tested on the PAD card
- Reagent: Chemical reagents applied in the lanes that interact with samples

RECOMMENDED WORKFLOW:
1. When analyzing a new card, first check project context for expected samples
2. Examine layout to understand lane arrangement and reagent positions
3. Use RGB analysis for quantitative color assessment in the barcode region
4. Connect observations to expected patterns based on samples in the project

TOOLS YOU SHOULD USE:
- download_ontology: Get full semantic structure of the PAD system
- compute_average_rgb: Analyze color values in specific regions of cards
- analyze_image_regions: Process multiple regions of an image with statistics
- get_api-ld_v3_cards_by-sample: Get comprehensive card data by sample ID
- get_api-ld_v3_projects: List available projects for context
- get_api-ld_v3_layout: Get geometric arrangements of lanes and fiducials
- get_api-ld_v3_project_by-name: Get detailed project information

ANALYSIS GUIDELINES:
- Report color variations quantitatively with RGB values from bounding boxes
- Connect observations to semantic meaning via ontology relationships
- Consider historical context within projects for comparative analysis
- Highlight unexpected patterns or anomalies in color development
"""


def pad_tool_reminders() -> List[UserMessage]:
    """
    Targeted reminders about available tools and when to use them.
    """
    return [
        UserMessage("""
IMPORTANT: Always use these tools when working with PAD card analysis:

1. FIRST STEP: Use download_ontology() to understand the PAD system's semantic structure
2. For any visual analysis, use analyze_image_regions(image_path, regions) or compute_average_rgb(bbox, image_path) for quantitative data
3. When discussing a specific card, use get_api-ld_v3_cards_by-sample to get its JSON-LD data
4. For project context, use get_api-ld_v3_projects and get_api-ld_v3_project_by-name
5. To understand card layouts, use get_api-ld_v3_layout to get geometric data

These tools provide semantic context that is ESSENTIAL for accurate analysis.

Always process a card in this order:
1. Get project context first
2. Understand the layout configuration
3. Analyze the image with appropriate bounding boxes
4. Connect findings to expected results based on the sample
""")
    ]


def analyze_pad_card(card_id: int, project_name: Optional[str] = None) -> List[AssistantMessage]:
    """
    Prompt template for analyzing a specific PAD card with context.
    """
    context = f"from project '{project_name}'" if project_name else ""
    
    return [
        AssistantMessage(f"""
I'll help analyze PAD card {card_id} {context}. To provide a comprehensive analysis, I'll use the following approach:

1. First, I'll use download_ontology() to refresh my understanding of the PAD system's structure
2. I'll retrieve the card's data using get_api-ld_v3_cards_by-sample
3. I'll examine the project context using get_api-ld_v3_project_by-name
4. I'll analyze the layout with get_api-ld_v3_layout to understand lane configurations
5. I'll download the Card image with get_api_ld_v3_cards_id_download_image to the local filesystem
6. I'll load the image from the local filesystem with load_image in a down-sized format (resize_image set to 300) to circumvent Claude image size restrictions
7. For color analysis, I'll use analyze_image_regions on the barcode region and key lanes

Would you like me to proceed with this analysis?
""")
    ]


def compare_pad_cards(card_id_1: int, card_id_2: int) -> List[UserMessage]:
    """
    Prompt template for comparing multiple PAD cards.
    """
    ids_str = ", ".join([str(card_id_1), str(card_id_2)])
     
    return [
        UserMessage(f"""
I need to compare the following PAD cards: {ids_str}

Please use the PAD tools to:
1. Get the ontology structure with download_ontology()
2. Retrieve data for each card using get_api-ld_v3_cards_by-sample
3. Determine if they're from the same project
4. Compare the color patterns using analyze_image_regions
5. Identify similarities and differences in their color barcodes

Please structure your analysis to show:
- Common project parameters
- RGB value comparisons by lane
- Interpretation of differences based on the ontology
""")
    ]


def project_overview(project_name: str) -> List[UserMessage]:
    """
    Prompt template for getting an overview of a specific project.
    """
    return [
        UserMessage(f"""
Please provide an overview of the PAD project "{project_name}".

Use these tools to gather information:
1. download_ontology() for semantic context
2. get_api-ld_v3_project_by-name for project details
3. get_api-ld_v3_cards_by-project_project_name_sample-ids to see all cards in the project

In your response, please include:
- The project's purpose and parameters
- Samples being tested
- Layout configuration used
- Number of cards in the project
- Any notes or special considerations
""")
    ]


def new_user_introduction() -> List[AssistantMessage]:
    """
    Introduction for new users to explain the PAD system.
    """
    return [
        AssistantMessage("""
Welcome to the PAD (Paper-based Analytical Device) system! I'm an AI assistant specialized in helping with PAD analysis.

The PAD system is used for chemical analysis, particularly for drug testing and identification. Here's a brief overview:

1. PAD cards contain multiple lanes with different reagents
2. When a sample is applied, chemical reactions create color patterns
3. These patterns form a "Color Barcode" that can identify substances
4. Projects organize multiple cards with defined parameters

I have access to several specialized tools to help analyze PAD data:
- Ontology access for understanding semantic relationships
- RGB analysis for quantitative color measurement
- JSON-LD API access for retrieving comprehensive data

How can I assist with your PAD research today? Would you like:
- An explanation of PAD concepts and terminology?
- Help analyzing specific card data?
- Assistance with project organization?
- Interpretation of color patterns?
""")
    ]


def debug_card_analysis(error_message: str) -> List[UserMessage]:
    """
    Prompt for debugging issues with card analysis.
    """
    return [
        UserMessage(f"""
I'm having trouble with PAD card analysis. Here's the error:

{error_message}

Please help me diagnose this issue by:
1. Using download_ontology() to check for any relevant constraints
2. Suggesting possible causes based on the PAD system structure
3. Recommending debugging steps using the available tools
4. Providing a workflow to verify the solution

Use the JSON-LD API tools to check for any data inconsistencies that might be causing this problem.
""")
    ]


def recommend_analysis_improvements() -> Dict[str, Any]:
    """
    Prompt for recommending improvements to PAD analysis workflow.
    """
    return {
        "messages": [
            {"role": "user", "content": """
Based on your experience with our PAD system and the available tools, what improvements would you recommend for our analysis workflow?

Consider:
- Additional data we should capture
- New tools that would enhance analysis
- Ways to better structure the semantic data
- Improvements to the ontology

Please use download_ontology() to reference the current system structure in your recommendations.
"""}
        ]
    }
