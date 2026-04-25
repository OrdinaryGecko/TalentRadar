# Sample Input And Output

## Sample JD

```text
Senior AI Engineer
Seniority: senior
Location: India
Work mode: Remote

Requirements:
- 5+ years of experience
- Python
- FastAPI
- LLMs
- pgvector

Nice to have:
- AWS
```

## Parsed Requirements

```json
{
  "role": "Senior AI Engineer",
  "seniority": "senior",
  "required_capabilities": ["Python", "FastAPI", "LLMs", "pgvector"],
  "preferred_capabilities": ["AWS"],
  "minimum_years_experience": 5,
  "location": "India",
  "work_mode": "remote"
}
```

## Ranked Shortlist

### 1. Aditi Rao

- `match_score`: `90.0`
- `interest_score`: `75.0`
- `combined_score`: `84.8`
- Why she ranks first:
  - covers all required capabilities
  - fits experience, location, and work mode
  - remains reasonably open to a move
  - loses some score because preferred `AWS` is missing

Conversation snapshot:

```text
Recruiter: Hi Aditi, I'm reaching out about a Senior AI Engineer opening. Your background in Python, FastAPI, LLMs looks relevant. Would you be open to a quick conversation?

Candidate: I'm not urgently looking, but I'm open to hearing more if the Senior AI Engineer role is hands-on and the problem space is strong.
```

### 2. Rahul Menon

- `match_score`: `73.3`
- `interest_score`: `80.0`
- `combined_score`: `75.6`
- Why he ranks second:
  - stronger interest than Aditi
  - matches preferred `AWS`
  - misses required `FastAPI` and `pgvector`, which keeps match score below the top candidate

### 3. Arjun Nair

- `match_score`: `63.3`
- `interest_score`: `51.0`
- `combined_score`: `59.0`
- Why he ranks third:
  - partial technical overlap
  - compensation sensitivity lowers recruiter confidence
  - lacks `FastAPI`, `pgvector`, and preferred `AWS`

## Interpretation

This sample run demonstrates the intended behavior:

- a candidate can rank first even without all preferred skills if required fit is strong
- a candidate with stronger interest can still outrank weaker-interest candidates when fit is reasonably close
- combined ranking is not the same as match-only sorting
