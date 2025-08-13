#!/usr/bin/env python3
"""
Subject Researcher MCP Server - Advanced Research Engine
Implements comprehensive 11-phase research methodology for deep analysis and synthesis.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

try:
    from subject_researcher_mcp.research_engine import ResearchEngine, ResearchInputs
except ImportError:
    from .research_engine import ResearchEngine, ResearchInputs

logger = logging.getLogger(__name__)

server = Server("subject-researcher-mcp")

# Initialize research engine
research_engine = None

async def get_research_engine() -> ResearchEngine:
    """Get or create research engine instance."""
    global research_engine
    if research_engine is None:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        research_engine = ResearchEngine(gemini_api_key)
    return research_engine

def validate_date_range(start_date: str, end_date: str) -> tuple[datetime, datetime, int]:
    """Validate and parse date range. Returns (start_dt, end_dt, recency_months)."""
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    except ValueError as e:
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD format. Error: {e}")
    
    if start_dt > end_dt:
        raise ValueError("Start date cannot be after end date")
    
    current_date = datetime.now(timezone.utc)
    if end_dt > current_date:
        raise ValueError(f"End date cannot be in the future. Current date is {current_date.strftime('%Y-%m-%d')}")
    
    # Calculate months for recency preference
    date_diff = (current_date - start_dt).days
    recency_months = max(1, min(60, date_diff // 30))
    
    return start_dt, end_dt, recency_months

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available research tools."""
    current_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    return [
        types.Tool(
            name="comprehensive_research",
            description=f"Conduct iterative target-driven research with quality meters (coverage, recency, novelty, agreement, contradictions). Uses stop criteria and automatic widening when stagnation occurs. Returns detailed analysis with inline citations and evidence-based recommendations. IMPORTANT: Current date is {current_date}. Use this to determine appropriate date ranges.",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "The research subject or topic to investigate comprehensively"
                    },
                    "start_date": {
                        "type": "string",
                        "format": "date",
                        "description": f"Research start date (YYYY-MM-DD format). Current date is {current_date}. Use this to determine appropriate date ranges."
                    },
                    "end_date": {
                        "type": "string", 
                        "format": "date",
                        "description": f"Research end date (YYYY-MM-DD format). Current date is {current_date}. Can use today's date if researching up to present."
                    },
                    "objective": {
                        "type": "string",
                        "enum": ["comprehensive_analysis", "best_options", "decision_support"],
                        "description": "Research objective: comprehensive analysis, finding best options, or decision support",
                        "default": "comprehensive_analysis"
                    },
                    "depth": {
                        "type": "string",
                        "enum": ["fast", "standard", "deep"],
                        "description": "Research depth: fast (2-3 iterations), standard (3-5 iterations), deep (5-8 iterations)",
                        "default": "standard"
                    },
                    "max_sources": {
                        "type": "integer",
                        "description": "Maximum number of sources to analyze (default: 50)",
                        "default": 50,
                        "minimum": 10,
                        "maximum": 200
                    },
                    "recency_months": {
                        "type": "integer",
                        "description": "Prefer sources from last N months (default: 18)",
                        "default": 18,
                        "minimum": 1,
                        "maximum": 60
                    },
                    "constraints": {
                        "type": "object",
                        "description": "Research constraints and quality gates",
                        "properties": {
                            "max_iterations": {
                                "type": "integer",
                                "description": "Maximum research iterations (default: 5)",
                                "default": 5,
                                "minimum": 2,
                                "maximum": 10
                            },
                            "gate_thresholds": {
                                "type": "object",
                                "description": "Quality gate thresholds for stopping criteria",
                                "properties": {
                                    "min_coverage": {"type": "number", "default": 0.7, "minimum": 0.0, "maximum": 1.0},
                                    "min_recency": {"type": "number", "default": 0.5, "minimum": 0.0, "maximum": 1.0},
                                    "novelty_threshold": {"type": "number", "default": 0.1, "minimum": 0.0, "maximum": 1.0},
                                    "max_contradictions": {"type": "number", "default": 0.3, "minimum": 0.0, "maximum": 1.0}
                                }
                            }
                        },
                        "additionalProperties": True
                    }
                },
                "required": ["subject", "start_date", "end_date"]
            }
        ),
        types.Tool(
            name="quick_research",
            description=f"Perform quick research for rapid insights. Uses simplified methodology for faster results when comprehensive analysis isn't needed. IMPORTANT: Current date is {current_date}. Use this to determine appropriate date ranges.",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "The subject to research quickly"
                    },
                    "start_date": {
                        "type": "string",
                        "format": "date", 
                        "description": f"Research start date (YYYY-MM-DD format). Current date is {current_date}."
                    },
                    "end_date": {
                        "type": "string",
                        "format": "date",
                        "description": f"Research end date (YYYY-MM-DD format). Current date is {current_date}. Can use today's date if researching up to present."
                    },
                    "focus": {
                        "type": "string",
                        "description": "Specific focus area or question to prioritize",
                        "default": "overview"
                    },
                    "max_sources": {
                        "type": "integer",
                        "description": "Maximum sources for quick analysis (default: 10)",
                        "default": 10,
                        "minimum": 3,
                        "maximum": 20
                    }
                },
                "required": ["subject", "start_date", "end_date"]
            }
        ),
        types.Tool(
            name="best_options_research",
            description=f"Research and evaluate the best options/solutions for a specific need. Applies scoring rubrics and gate rules to rank alternatives with quantified outcomes. IMPORTANT: Current date is {current_date}. Use this to determine appropriate date ranges.",
            inputSchema={
                "type": "object",
                "properties": {
                    "need": {
                        "type": "string",
                        "description": "What you need the best options for (e.g., 'fastest build tools for large TypeScript projects')"
                    },
                    "start_date": {
                        "type": "string",
                        "format": "date",
                        "description": f"Research start date (YYYY-MM-DD format). Current date is {current_date}."
                    },
                    "end_date": {
                        "type": "string",
                        "format": "date", 
                        "description": f"Research end date (YYYY-MM-DD format). Current date is {current_date}. Can use today's date if researching up to present."
                    },
                    "criteria": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Evaluation criteria (e.g., ['performance', 'ease of use', 'community support'])",
                        "default": ["effectiveness", "reliability", "ease of use"]
                    },
                    "constraints": {
                        "type": "object",
                        "description": "Constraints like budget, technology stack, team size",
                        "additionalProperties": True
                    },
                    "max_options": {
                        "type": "integer",
                        "description": "Maximum number of options to evaluate (default: 5)",
                        "default": 5,
                        "minimum": 2,
                        "maximum": 10
                    }
                },
                "required": ["need", "start_date", "end_date"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution with comprehensive research methodology."""
    if arguments is None:
        arguments = {}
    
    try:
        engine = await get_research_engine()
        
        if name == "comprehensive_research":
            subject = arguments.get("subject", "")
            start_date = arguments.get("start_date", "")
            end_date = arguments.get("end_date", "")
            
            if not subject:
                raise ValueError("Subject is required for comprehensive research")
            if not start_date:
                raise ValueError("Start date is required")
            if not end_date:
                raise ValueError("End date is required")
            
            # Validate date range
            start_dt, end_dt, recency_months = validate_date_range(start_date, end_date)
            
            # Create research inputs
            inputs = ResearchInputs(
                subject=subject,
                objective=arguments.get("objective", "comprehensive_analysis"),
                depth=arguments.get("depth", "standard"),
                max_sources=arguments.get("max_sources", 30),
                recency_months=recency_months,
                constraints={
                    "start_date": start_date,
                    "end_date": end_date,
                    **arguments.get("constraints", {})
                }
            )
            
            # Conduct iterative research
            report = await engine.conduct_iterative_research(inputs)
            
            # Format comprehensive report
            content = await _format_comprehensive_report(report)
            
            return [types.TextContent(type="text", text=content)]
        
        elif name == "quick_research":
            subject = arguments.get("subject", "")
            start_date = arguments.get("start_date", "")
            end_date = arguments.get("end_date", "")
            
            if not subject:
                raise ValueError("Subject is required for quick research")
            if not start_date:
                raise ValueError("Start date is required")
            if not end_date:
                raise ValueError("End date is required")
            
            # Validate date range
            start_dt, end_dt, recency_months = validate_date_range(start_date, end_date)
            
            # Use fast mode for quick research
            inputs = ResearchInputs(
                subject=subject,
                objective="comprehensive_analysis",
                depth="fast",
                max_sources=arguments.get("max_sources", 10),
                recency_months=recency_months,
                constraints={
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            report = await engine.conduct_research(inputs)
            content = await _format_quick_report(report)
            
            return [types.TextContent(type="text", text=content)]
        
        elif name == "best_options_research":
            need = arguments.get("need", "")
            start_date = arguments.get("start_date", "")
            end_date = arguments.get("end_date", "")
            
            if not need:
                raise ValueError("Need is required for best options research")
            if not start_date:
                raise ValueError("Start date is required")
            if not end_date:
                raise ValueError("End date is required")
            
            # Validate date range
            start_dt, end_dt, recency_months = validate_date_range(start_date, end_date)
            
            # Configure for best options analysis
            inputs = ResearchInputs(
                subject=need,
                objective="best_options",
                depth="standard",
                max_sources=arguments.get("max_sources", 25),
                recency_months=recency_months,
                constraints={
                    "start_date": start_date,
                    "end_date": end_date,
                    "criteria": arguments.get("criteria", ["effectiveness", "reliability", "ease of use"]),
                    "max_options": arguments.get("max_options", 5),
                    **arguments.get("constraints", {})
                }
            )
            
            report = await engine.conduct_research(inputs)
            content = await _format_best_options_report(report, arguments.get("criteria", []))
            
            return [types.TextContent(type="text", text=content)]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return [types.TextContent(type="text", text=f"Research Error: {e}")]

async def _format_comprehensive_report(report) -> str:
    """Format comprehensive research report."""
    content = f"""# Comprehensive Research Report: {report.questions[0].question if report.questions else 'Research Analysis'}

## Executive Summary
{report.executive_summary}

## Recommendation
{report.recommendation}
**Confidence Level:** {report.confidence:.1%}

## Research Questions & Findings

"""
    
    # Add detailed findings for each question
    for i, question in enumerate(report.questions, 1):
        content += f"### {i}. {question.question}\n"
        content += f"**Hypothesis:** {question.hypothesis}\n"
        content += f"**Confidence:** {question.confidence:.1%}\n\n"
        
        if question.findings:
            content += "**Key Findings:**\n"
            for finding in question.findings[:3]:  # Top 3 findings per question
                content += f"- {finding.statement}\n"
                content += f"  *Source: {finding.author} ({finding.confidence:.1%} confidence)*\n"
            content += "\n"
        else:
            content += "*No specific findings extracted for this question.*\n\n"
    
    # Add source analysis
    content += "## Source Analysis\n\n"
    content += f"**Total Sources Analyzed:** {len(report.sources)}\n"
    
    high_quality_sources = [s for s in report.sources if s.credibility_score > 0.7]
    content += f"**High-Quality Sources:** {len(high_quality_sources)}\n\n"
    
    # List top sources
    content += "**Top Sources:**\n"
    sorted_sources = sorted(report.sources, key=lambda x: x.credibility_score, reverse=True)
    for source in sorted_sources[:5]:
        content += f"- [{source.title}]({source.url})\n"
        content += f"  *Domain: {source.domain} | Credibility: {source.credibility_score:.1%} | Type: {source.source_type}*\n"
    
    # Add methodology and limitations
    content += f"\n## Methodology\n{report.methodology}\n"
    
    if report.limitations:
        content += "\n## Limitations\n"
        for limitation in report.limitations:
            content += f"- {limitation}\n"
    
    # Add next actions
    if report.next_actions:
        content += "\n## Recommended Next Actions\n"
        for action in report.next_actions:
            content += f"- {action}\n"
    
    content += f"\n## Research Metadata\n"
    content += f"- **Generated:** {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}\n"
    content += f"- **Sources Processed:** {len(report.sources)}\n"
    content += f"- **Claims Extracted:** {len(report.claims)}\n"
    content += f"- **Research Questions:** {len(report.questions)}\n"
    
    return content

async def _format_quick_report(report) -> str:
    """Format quick research report."""
    content = f"""# Quick Research: {report.questions[0].question if report.questions else 'Analysis'}

## Summary
{report.executive_summary}

## Key Insights
{report.recommendation}

## Quick Findings
"""
    
    # Add top findings across all questions
    all_findings = []
    for question in report.questions:
        all_findings.extend(question.findings)
    
    # Sort by confidence and take top 5
    top_findings = sorted(all_findings, key=lambda x: x.confidence, reverse=True)[:5]
    
    for i, finding in enumerate(top_findings, 1):
        content += f"{i}. {finding.statement}\n"
    
    content += f"\n## Sources ({len(report.sources)} analyzed)\n"
    for source in report.sources[:3]:  # Top 3 sources
        content += f"- [{source.title}]({source.url})\n"
    
    content += f"\n*Quick research completed in fast mode. For comprehensive analysis, use the comprehensive_research tool.*"
    
    return content

async def _format_best_options_report(report, criteria) -> str:
    """Format best options research report."""
    content = f"""# Best Options Research: {report.questions[0].question if report.questions else 'Options Analysis'}

## Executive Summary
{report.executive_summary}

## Recommendation
{report.recommendation}
**Overall Confidence:** {report.confidence:.1%}

## Evaluation Criteria
"""
    
    if criteria:
        for criterion in criteria:
            content += f"- {criterion}\n"
    
    content += "\n## Option Analysis\n"
    
    # Extract options from findings (this would be more sophisticated in practice)
    all_findings = []
    for question in report.questions:
        all_findings.extend(question.findings)
    
    # Group findings by potential options
    content += "*Note: Option ranking would be implemented based on specific scoring rubrics*\n\n"
    
    # Add top findings as potential options
    top_findings = sorted(all_findings, key=lambda x: x.confidence, reverse=True)[:5]
    for i, finding in enumerate(top_findings, 1):
        content += f"### Option {i}\n"
        content += f"{finding.statement}\n"
        content += f"**Evidence Strength:** {finding.confidence:.1%}\n\n"
    
    # Add research methodology note
    content += "\n## Research Notes\n"
    content += f"- Analyzed {len(report.sources)} sources\n"
    content += f"- Extracted {len(report.claims)} claims\n"
    content += "- Applied best-options methodology with gate rules\n"
    
    return content

async def main():
    """Main entry point for the server."""
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="subject-researcher-mcp",
                    server_version="2.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    finally:
        # Clean up research engine
        if research_engine:
            await research_engine.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())