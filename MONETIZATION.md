# PTIL Monetization Plan

## Product Positioning

**One-liner:** "Fast semantic encoding for intent classification, search, and deduplication."

**Not:** "Better training data for LLMs" (no proof)
**Not:** "40% cost reduction" (fabricated)

**Actually:** A fast semantic encoder that converts text to structured codes for routing, search, and dedup.

## Pricing Tiers

### Free Tier
- **Price:** $0
- **Limits:** 1,000 texts/day, English only
- **Features:** Ultra-compact encoding, basic API
- **Goal:** Get developers to try it

### Pro Tier
- **Price:** $49/month
- **Limits:** 100,000 texts/day, 5 languages
- **Features:** All serialization formats, batch API, priority support
- **Goal:** Small businesses, indie developers

### Business Tier
- **Price:** $199/month
- **Limits:** 1,000,000 texts/day, all languages
- **Features:** Custom ROOT mappings, analytics dashboard, SLA
- **Goal:** SaaS companies, e-commerce

### Enterprise Tier
- **Price:** Custom (contact sales)
- **Limits:** Unlimited
- **Features:** On-premise deployment, custom training, dedicated support
- **Goal:** Large companies

## Revenue Streams

### 1. API Usage (Primary)
- Per-text pricing after free tier
- $0.001 per text (1,000 texts = $1)
- Volume discounts at 100K+ texts

### 2. Self-Hosted License
- One-time fee for on-premise deployment
- $999 for small teams
- $4,999 for enterprises

### 3. Custom Training
- Train custom ROOT mappings for specific domains
- $2,000 per domain

### 4. Support Plans
- Basic: Free (community)
- Priority: $49/month (24hr response)
- Dedicated: $199/month (1hr response)

## What Needs To Be Built

### Phase 1: Core Product (Week 1-2)
- [x] Semantic encoder (done)
- [x] REST API (done)
- [x] CLI (done)
- [ ] Intent classification endpoint
- [ ] Batch processing endpoint
- [ ] Usage tracking / billing

### Phase 2: Demo & Marketing (Week 3-4)
- [ ] Live demo website
- [ ] Intent classification demo
- [ ] Semantic search demo
- [ ] Chatbot router demo

### Phase 3: Sales (Week 5-6)
- [ ] Stripe integration
- [ ] User dashboard
- [ ] Analytics page
- [ ] Documentation site

## Target Customers

### Customer 1: SaaS Chatbots
- **Problem:** Route 10K+ daily messages to correct departments
- **Solution:** Intent classification via CSC ROOT codes
- **Price:** $199/month

### Customer 2: E-commerce Search
- **Problem:** Product deduplication, semantic search
- **Solution:** Ultra-compact CSC for similarity matching
- **Price:** $199/month

### Customer 3: Customer Support
- **Problem:** Auto-categorize support tickets
- **Solution:** Intent classification + priority detection
- **Price:** $99/month

### Customer 4: NLP Developers
- **Problem:** Need fast semantic features for their apps
- **Solution:** CSC as feature extraction API
- **Price:** $49/month

## Sales Channels

### 1. Product Hunt Launch
- Target: Top 5 product of the day
- Demo: Live intent classification
- Offer: 3 months free Pro tier

### 2. Developer Communities
- Reddit: r/MachineLearning, r/Python, r/LocalLLaMA
- Hacker News: Show HN post
- Dev.to: Technical tutorial

### 3. Content Marketing
- Blog: "How to Build Intent Classification in 5 Minutes"
- YouTube: Live demo video
- Twitter: Thread with examples

### 4. Direct Outreach
- SaaS companies with chatbots
- E-commerce platforms
- Customer support tools

## Revenue Projections (Conservative)

| Month | Users | Paying | MRR |
|-------|-------|--------|-----|
| 1 | 100 | 5 | $245 |
| 2 | 300 | 15 | $735 |
| 3 | 500 | 30 | $1,470 |
| 6 | 1,000 | 60 | $2,940 |
| 12 | 2,000 | 120 | $5,880 |

## Key Metrics to Track

1. **API calls/day** — usage growth
2. **Conversion rate** — free to paid
3. **Churn rate** — monthly retention
4. **ARPU** — average revenue per user
5. **LTV** — customer lifetime value

## Launch Checklist

- [ ] README rewritten (done)
- [ ] Intent classification endpoint
- [ ] Usage tracking
- [ ] Stripe billing
- [ ] Demo website
- [ ] Product Hunt page
- [ ] Hacker News post
- [ ] Twitter thread
