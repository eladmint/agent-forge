# Claude Desktop Test Scenarios

This document contains comprehensive test scenarios for validating Agent Forge MCP integration with Claude Desktop.

## Test Scenario Categories


### Information

#### Basic Agent Info Query (beginner)
**Description:** User wants to see available Agent Forge capabilities

**User Command:**
```
Claude, use get_agent_info to show me all available Agent Forge tools and their capabilities
```

**Expected Tool:** `get_agent_info`

---


### Web Automation

#### Website Navigation Request (intermediate)
**Description:** User wants to navigate and extract content from a website

**User Command:**
```
Use navigate_website to visit TechCrunch and extract the top 3 headlines from the homepage
```

**Expected Tool:** `navigate_website`

**Expected Parameters:**
```json
{
  "url": "https://techcrunch.com",
  "extraction_target": "content"
}
```

---


### Blockchain

#### Blockchain Proof Generation (advanced)
**Description:** User wants to create a blockchain proof for verification

**User Command:**
```
Generate a blockchain proof for my comprehensive analysis of Apple's homepage accessibility and performance
```

**Expected Tool:** `generate_blockchain_proof`

**Expected Parameters:**
```json
{
  "task_description": "comprehensive analysis of Apple's homepage accessibility and performance"
}
```

---


### Data Analysis

#### Multi-Source Data Compilation (intermediate)
**Description:** User wants to compile data from multiple sources

**User Command:**
```
Use compile_data_from_sources to gather pricing information from these 3 competitor websites and create a comparison table
```

**Expected Tool:** `compile_data_from_sources`

**Expected Parameters:**
```json
{
  "sources": [
    "competitor1.com",
    "competitor2.com",
    "competitor3.com"
  ],
  "instructions": "gather pricing information and create a comparison table"
}
```

---


### Content Processing

#### Content Extraction Request (intermediate)
**Description:** User wants to extract clean content from an article

**User Command:**
```
Use extract_text_content to get the full article text from this research paper URL and format it as clean markdown
```

**Expected Tool:** `extract_text_content`

**Expected Parameters:**
```json
{
  "url": "https://arxiv.org/abs/2024.12345",
  "content_type": "article",
  "include_metadata": true
}
```

---


### Validation

#### Website Validation Request (intermediate)
**Description:** User wants to validate website for accessibility issues

**User Command:**
```
Run validate_website_data on our company website to check for accessibility issues and provide improvement recommendations
```

**Expected Tool:** `validate_website_data`

**Expected Parameters:**
```json
{
  "url": "company_website_url",
  "check_accessibility": true
}
```

---


### Workflow

#### Complex Multi-Tool Workflow (advanced)
**Description:** User wants to use multiple tools in sequence

**User Command:**
```
First use navigate_website to analyze Tesla.com homepage, then validate_website_data to check for issues, and finally generate_blockchain_proof to create a verification record
```

---


### Interpretation

#### Natural Language Ambiguous Request (advanced)
**Description:** User makes a vague request that needs interpretation

**User Command:**
```
Help me research my competitors and create a report
```

---


### Error Handling

#### Error Recovery Scenario (intermediate)
**Description:** User provides invalid URL or parameters

**User Command:**
```
Use navigate_website to visit not-a-real-website-url-123.com
```

**Expected Tool:** `navigate_website`

---


### Performance

#### Performance Intensive Request (advanced)
**Description:** User requests processing of multiple large sources

**User Command:**
```
Use the data_compiler agent to analyze these 10 market research reports and identify common trends
```

**Expected Tool:** `data_compiler`

---


## Usage Instructions

1. **Setup Claude Desktop** with Agent Forge MCP configuration
2. **Test each scenario** by copying the user command into Claude Desktop
3. **Verify responses** match expected tools and response elements
4. **Check error handling** for scenarios marked with error handling
5. **Monitor performance** for scenarios with performance considerations

## Success Criteria

- ✅ All tools respond correctly to natural language commands
- ✅ Parameters are extracted accurately from conversational input
- ✅ Error scenarios are handled gracefully
- ✅ Performance scenarios complete within expected timeframes
- ✅ Multi-tool workflows execute in proper sequence
