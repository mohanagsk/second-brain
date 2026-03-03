# Instagram Scraping Tool Comparison Analysis

**Analysis Date:** March 3, 2026  
**Data Source:** Apify Instagram Reels Scraper  
**Sample Size:** 160 reels (100 + 30 + 30) from 3 accounts

---

## 1. Apify Field Inventory

### Account-Level Metadata
- `username` - Account username (string)
- `scraped_at` - Timestamp of scraping (ISO 8601)
- `total_reels` - Total reels scraped (integer)
- `avg_plays` - Average view count (integer)
- `avg_engagement` - Average engagement (integer)
- `outliers_count` - Number of viral reels (integer)
- `underperformers_count` - Number of low-performing reels (integer)

### Reel-Level Data (Per Item)
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Instagram media ID |
| `shortCode` | string | URL identifier |
| `url` | string | Full reel URL |
| `caption` | string | Post caption text |
| `hashtags` | array | Extracted hashtags |
| **`plays`** | **integer** | **View count (CRITICAL)** |
| `likes` | integer | Like count |
| `comments` | integer | Comment count |
| `engagement` | integer | Total engagement (likes + comments) |
| `timestamp` | string | Post date (ISO 8601) |
| `duration` | float | Video length in seconds |
| `transcript` | string/null | Video transcript (if available) |
| `videoUrl` | string | Direct video download URL |
| `outlier_score` | float | Performance multiplier |
| `engagement_rate` | float | Engagement as % of views |

**Total Fields:** 16 per reel + 7 account-level = **23 data points**

---

## 2. Data Quality Assessment

### 2.1 Null Value Analysis

| Field | Null Count | Null % | Notes |
|-------|-----------|--------|-------|
| `transcript` | 160/160 | 100% | ⚠️ Always null - feature not working |
| `caption` | 0/160 | 0% | ✅ Complete |
| `plays` | 0/160 | 0% | ✅ Complete |
| `likes` | 0/160 | 0% | ✅ Complete |
| `comments` | 0/160 | 0% | ✅ Complete |
| `hashtags` | 0/160 | 0% | ✅ Complete (empty arrays exist) |
| `videoUrl` | 0/160 | 0% | ✅ Complete |
| `timestamp` | 0/160 | 0% | ✅ Complete |

### 2.2 Data Consistency

✅ **Excellent Consistency:**
- All numeric fields properly typed
- Timestamps in consistent ISO 8601 format
- URLs well-formed and valid
- Engagement calculation accurate: `engagement = likes + comments`
- Engagement rate properly calculated: `(engagement / plays) * 100`

⚠️ **Issues Found:**
1. **Transcript field:** 100% null - feature appears broken or unavailable
2. **Caption truncation:** Some captions appear cut off mid-sentence
3. **VideoUrl expiration:** These are CDN URLs that likely expire (Instagram's limitation)

### 2.3 Missing Fields vs Real Instagram Data

**Available in Apify:**
- Views (plays) ✅
- Likes ✅
- Comments ✅
- Video duration ✅
- Post date ✅
- Direct video URL ✅

**Missing from Apify:**
- Shares count ❌
- Saves count ❌
- Profile visits from reel ❌
- Reach metrics ❌
- Audience retention graph ❌

*Note: Missing fields are only available via Instagram's Creator API/Insights, not public scraping*

---

## 3. Tool Comparison Matrix

| Feature | Apify | yt-dlp | Instaloader (theoretical) |
|---------|-------|--------|---------------------------|
| **Core Metrics** |
| Views (plays) | ✅ Yes | ❌ No | ✅ Yes |
| Likes | ✅ Yes | ✅ Yes | ✅ Yes |
| Comments count | ✅ Yes | ✅ Yes | ✅ Yes |
| Video duration | ✅ Yes | ✅ Yes | ✅ Yes |
| Post timestamp | ✅ Yes | ✅ Yes | ✅ Yes |
| **Content** |
| Caption text | ✅ Yes | ✅ Yes | ✅ Yes |
| Hashtags (parsed) | ✅ Array | ⚠️ In caption | ✅ Array |
| Video URL | ✅ Direct CDN | ✅ Direct | ✅ Direct |
| Transcript | ❌ Broken | ❌ No | ❌ No |
| **Advanced Metrics** |
| Engagement rate | ✅ Calculated | ❌ No | ⚠️ Manual calc |
| Outlier detection | ✅ Yes | ❌ No | ❌ No |
| Performance scoring | ✅ Yes | ❌ No | ❌ No |
| **Technical** |
| Account summary | ✅ Yes | ❌ No | ✅ Yes |
| JSON output | ✅ Yes | ✅ Yes | ✅ Yes |
| Batch scraping | ✅ Yes | ⚠️ Manual | ✅ Yes |
| Rate limiting | ✅ Handled | ❌ Manual | ⚠️ Basic |
| Login required | ❌ No | ❌ No | ✅ Yes* |
| Current status | ✅ Working | ✅ Working | ❌ **Blocked** |

*Instaloader theoretically requires login but is currently blocked by Instagram

---

## 4. Tool Scoring (Out of 100)

### Apify: **88/100** ⭐⭐⭐⭐

**Strengths:**
- ✅ **Most complete data** - includes critical `plays` (views) field
- ✅ Pre-calculated analytics (engagement rate, outlier scores)
- ✅ No authentication required
- ✅ Handles rate limiting automatically
- ✅ Clean, consistent JSON structure
- ✅ Account-level summaries included
- ✅ Bulk scraping support

**Weaknesses:**
- ❌ Transcript field broken (100% null)
- ❌ Paid service (costs money per scrape)
- ❌ Some caption truncation
- ⚠️ Video URLs expire (Instagram's limitation)

**Breakdown:**
- Data completeness: 20/25 (-5 for broken transcript)
- Data quality: 25/25
- Analytics features: 20/20
- Ease of use: 18/20 (-2 for cost barrier)
- Reliability: 5/10 (requires API key, paid credits)

---

### yt-dlp: **62/100** ⭐⭐⭐

**Strengths:**
- ✅ Free and open-source
- ✅ Downloads video files
- ✅ Good metadata extraction
- ✅ Active development
- ✅ Works without authentication

**Weaknesses:**
- ❌ **Missing views (plays) data** - CRITICAL for content analysis
- ❌ No hashtag parsing
- ❌ No engagement rate calculation
- ❌ No bulk account scraping
- ❌ Manual rate limiting required
- ❌ No analytics features

**Breakdown:**
- Data completeness: 12/25 (-13 for missing views!)
- Data quality: 20/25 (-5 for missing key metric)
- Analytics features: 0/20
- Ease of use: 20/20
- Reliability: 10/10

---

### Instaloader: **45/100** ⭐⭐ (Estimated)

**Strengths (When Working):**
- ✅ Comprehensive field extraction
- ✅ Includes views data
- ✅ Profile/account scraping
- ✅ Free and open-source
- ✅ Active community

**Weaknesses:**
- ❌ **Currently BLOCKED by Instagram** 🚫
- ❌ Requires login (account risk)
- ❌ Aggressive rate limiting
- ❌ Frequent API changes break tool
- ❌ No built-in analytics
- ⚠️ Accounts get banned/restricted

**Breakdown:**
- Data completeness: 20/25 (when working)
- Data quality: 20/25 (when working)
- Analytics features: 5/20
- Ease of use: 0/20 (-20 for being blocked)
- Reliability: 0/10 (**not functional**)

---

## 5. Comparison Summary

### Critical Differentiator: VIEWS DATA

| Tool | Views Available? | Impact |
|------|------------------|--------|
| Apify | ✅ **YES** (`plays` field) | Can calculate engagement rates, identify viral content |
| yt-dlp | ❌ **NO** | Cannot analyze performance, missing critical metric |
| Instaloader | ✅ Yes (when working) | Currently blocked - 0% success rate |

**Verdict:** Apify is the ONLY currently working tool that provides view counts.

---

## 6. Use Case Recommendations

### For Content Intelligence (Views Critical)
**Winner: Apify** 🏆
- **Use when:** You need view counts, engagement analysis, bulk scraping
- **Cost:** ~$0.10-0.50 per 100 reels (varies by account size)
- **Pros:** Complete data, reliable, no account risk
- **Cons:** Costs money

### For Video Archival (Views Not Critical)
**Winner: yt-dlp** 🥈
- **Use when:** Downloading videos, free tool required
- **Cost:** Free
- **Pros:** Downloads actual video files, metadata included
- **Cons:** No view counts - limited analytics

### For Experimentation Only
**Avoid: Instaloader** 🚫
- **Status:** Currently blocked
- **Risk:** Account bans
- **Recommendation:** Wait for Instagram to unblock or tool updates

---

## 7. Data Quality Report Card

| Category | Apify | yt-dlp | Instaloader |
|----------|-------|--------|-------------|
| Completeness | A- | C+ | N/A |
| Consistency | A+ | A | N/A |
| Accuracy | A | A | N/A |
| Reliability | B+ | A | F |
| Value | B | A+ | F |
| **Overall** | **A-** | **B** | **F** |

---

## 8. Final Recommendation

### Primary Tool: **Apify**
For Instagram Intel and content analysis, Apify is the clear winner:
- ✅ Only tool providing views data (critical!)
- ✅ Clean, analyzable JSON output
- ✅ Pre-calculated analytics save development time
- ✅ Reliable and currently working
- ⚠️ Costs money but worth it for complete data

### Backup Tool: **yt-dlp**
Keep as fallback for:
- Video downloads
- Basic metadata when budget is $0
- Testing/development without API costs

### Avoid: **Instaloader**
- Currently blocked
- Not worth the account ban risk
- Re-evaluate when Instagram unblocks

---

## 9. Technical Notes

### Apify Video URL Handling
```json
"videoUrl": "https://scontent-iad3-2.cdninstagram.com/o1/v/t16/..."
```
- These are temporary CDN URLs
- Expire after ~6-48 hours
- Must download videos immediately or store permanent copies
- Instagram's security feature, not Apify limitation

### Sample Data Verification
**Account: divy.kairoth**
- Viral reel: 3.09M views (DSb1mrUkVxo)
- Average: 57,353 views
- Outlier threshold working correctly (53.85x multiplier)

**Account: vedikabhaia**
- Massive outlier: 19.04M views (DSb1mrUkVxo) - 20.61x average
- Average: 923,499 views
- Clean data distribution

**Account: jaykapoor.24**
- Top performer: 6.43M views (DB1KsODvC2a)
- Average: 937,458 views
- Consistent field quality across all reels

---

## 10. Conclusion

**Apify is the recommended tool for Instagram Intel.** 

While it costs money, the complete dataset (especially views) and pre-calculated analytics make it worth the investment. The 88/100 score reflects high data quality with only minor issues (broken transcript field).

yt-dlp remains useful for video archival but is inadequate for content intelligence due to missing view counts.

Instaloader should be avoided until Instagram unblocks it.

**Cost-Benefit:** Spending ~$10-20/month on Apify saves dozens of hours of development and provides data that's impossible to get with free tools.

---

*Analysis completed: March 3, 2026*  
*Data samples: 160 reels across 3 accounts*  
*Next review: When Instagram APIs change or new tools emerge*
