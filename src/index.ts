import { FastMCP } from "fastmcp";
import { z } from "zod";
import { search } from "duck-duck-scrape";

const server = new FastMCP({
  name: "Subject Researcher MCP",
  version: "1.0.0",
  description: "Research any subject using DuckDuckGo and Gemini AI"
});

// DuckDuckGo search tool
server.addTool({
  name: "research_subject",
  description: "Research a subject using DuckDuckGo search",
  parameters: z.object({
    query: z.string().describe("The subject or topic to research"),
    maxResults: z.number().optional().default(5).describe("Maximum number of results to return")
  }),
  annotations: {
    title: "Subject Research Tool",
    readOnlyHint: true,
    openWorldHint: true
  },
  execute: async (args) => {
    try {
      const searchResults = await search(args.query, {
        safeSearch: "Strict"
      });
      
      const results = searchResults.results
        .slice(0, args.maxResults)
        .map(result => ({
          title: result.title,
          description: result.description,
          url: result.url
        }));
      
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            query: args.query,
            results: results,
            totalResults: results.length
          }, null, 2)
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: `Error researching subject: ${error instanceof Error ? error.message : "Unknown error"}`
        }]
      };
    }
  }
});

// Simple DuckDuckGo search tool
server.addTool({
  name: "duckduckgo_search",
  description: "Perform a simple DuckDuckGo search",
  parameters: z.object({
    query: z.string().describe("The search query"),
    region: z.string().optional().default("en-us").describe("The region for search results")
  }),
  annotations: {
    title: "DuckDuckGo Search",
    readOnlyHint: true,
    openWorldHint: true
  },
  execute: async (args) => {
    try {
      const searchResults = await search(args.query, {
        safeSearch: "Strict"
      });
      
      const formattedResults = searchResults.results
        .slice(0, 5)
        .map((result, index) => {
          return `${index + 1}. ${result.title}
           ${result.description}
           URL: ${result.url}`;
        })
        .join("\n\n");
      
      return `Search Results for "${args.query}":

${formattedResults}`;
    } catch (error) {
      return `Error performing search: ${error instanceof Error ? error.message : "Unknown error"}`;
    }
  }
});

// Start the server
server.start({
  transportType: "stdio"
});

console.log("Subject Researcher MCP Server started!");