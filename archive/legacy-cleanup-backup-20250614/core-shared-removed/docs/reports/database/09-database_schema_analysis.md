# Database Schema Analysis

## Events Table Structure

The `events` table has 22 columns:

### Primary Fields
- `id` (UUID) - Primary key
- `name` (string) - Event name
- `description` (text) - Event description
- `category` (string) - Event category
- `luma_url` (string) - Original Luma event URL
- `external_url` (string) - External event URL
- `created_at`, `updated_at` (timestamps)

### Event Details
- `location_name` (string) - Venue name
- `location_address` (string) - Full address
- `start_time_iso`, `end_time_iso` (datetime) - Event timing
- `timezone` (string) - Event timezone
- `cost` (string) - Event cost information
- `cost_category` (string) - Cost classification

### Event Metrics
- `estimated_attendee_count` (integer) - Expected attendance
- `networking_score` (integer) - Networking value score
- `exclusivity_score` (integer) - Event exclusivity rating

### Social & Links
- `event_social_links` (JSON) - Social media links
- `embedding` (vector) - Vector embedding for semantic search
- `fts` (text) - Full-text search field

### Raw Data
- `raw_scraped_data` (JSON) - Complete scraped data structure

## Raw Scraped Data Structure

The `raw_scraped_data` field contains comprehensive event information:

### Top-level fields:
- `url` - Event URL
- `conference` - Conference name (e.g., "EthCC")
- `event_name` - Full event name
- `description` - Event description
- `event_category` - Category classification
- `scraped_at` - Timestamp
- `source_url` - Original source

### Nested `raw_scraped_data` object:
- `method` - Scraping method used
- `location` - Location information
- `date_info` - Date/time details
- `relevance_score` - Event relevance (1-10)
- `is_ethcc_related` - Boolean flag

### Enhanced data (`quick_enhancement`):
- `event_type` - Type classification
- `technical_level` - Technical complexity
- `enhanced_metadata` - AI-enhanced details
- `enhancement_method` - Enhancement approach
- `enhancement_timestamp` - When enhanced

### Available Event Data Examples

#### Speaker Information:
- `speakers[]` - Array of speaker objects with:
  - `name` - Speaker name
  - `title` - Job title
  - `organization` - Company/org
  - `url` - Profile URL
- `presenter_name`, `presenter_url` - Primary presenter
- `primary_host_name`, `primary_host_url` - Event host

#### Venue Details:
- `location_name` - Venue name
- `location_address` - Full address
- Nested location data in raw_scraped_data

#### Social & Media:
- `event_social_media_links[]` - Social links
- `primary_host_social_links[]` - Host social media
- `presenter_social_links[]` - Speaker social media
- `image_derived_partners[]` - Partners from images

#### External Scraping Status:
- `external_scrape_status` - Additional scraping results
- Various status flags and metadata

## EthCC Events Analysis

Found 5 EthCC events in database:
1. **EthCC Brussels 2025** - Main conference
2. **EthCC Scaling Solutions Panel** - Technical panel
3. **EthCC After Party** - Community celebration
4. **EthCC Community Gathering** - ZK workshop
5. **EthCC Networking Event** - Developer day

### Data Quality:
- ✅ All have `raw_scraped_data` with comprehensive structure
- ✅ All have proper categorization (`category: "EthCC Event"`)
- ✅ All have enhanced metadata via AI processing
- ❌ Missing: `start_time_iso`, `end_time_iso`, `location_address`
- ❌ Limited: Image data (mostly empty arrays)

## Recommendations for Test Scripts

### 1. Use Available Data Fields
```python
# Query events with proper field selection
events = supabase.table('events').select(
    'id, name, description, category, luma_url, raw_scraped_data'
).ilike('category', '%ethcc%').execute()
```

### 2. Access Nested Data Properly
```python
# Extract data from raw_scraped_data
raw_data = event['raw_scraped_data']
speakers = raw_data.get('speakers', [])
location = raw_data.get('location_name', '')
description = raw_data.get('description', event['description'])
```

### 3. Test with Real Data Structure
- Use `raw_scraped_data.speakers[]` for speaker analysis
- Use `raw_scraped_data.location_name` for venue info
- Use `raw_scraped_data.description` for content analysis
- Use `quick_enhancement` for AI metadata testing

### 4. Handle Missing Fields Gracefully
- Most location/timing fields are None
- Image arrays are mostly empty
- Use fallback values from raw_scraped_data

### 5. Focus on Available Rich Data
- Speaker information (name, title, organization)
- Event descriptions and categories
- Host/presenter details
- Social media links
- Enhanced metadata from AI processing