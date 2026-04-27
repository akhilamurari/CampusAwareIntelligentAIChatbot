# CampusAware AI — User Testing Plan
## Sprint 5 — CF1CT-29

---

## Testing Overview
- **Date:** TBD
- **Location:** La Trobe Bundoora Campus
- **Participants:** 10+ La Trobe students
- **Duration:** 15-20 minutes per session
- **Tester:** Akhila Murari (Scrum Master)

---

## Pre-Testing Setup Checklist
- [ ] Server running (aiotcentre-03 vLLM)
- [ ] SSH tunnel active
- [ ] Streamlit app running on laptop
- [ ] Screen sharing ready
- [ ] Consent form printed/digital
- [ ] SUS survey link ready (Tarun's task)

---

## Test Scenario 1 — Room Conditions (NL2SQL)
Ask the participant to find answers to:

1. "Which room had the highest CO2 levels today?"
2. "Find me a quiet room to study right now"
3. "What is the temperature in the library?"
4. "Which rooms are currently occupied?"
5. "What is the air quality in Lab-101?"
6. "Which room has the lowest noise level?"
7. "Is Meeting-Room-1 available right now?"
8. "What is the humidity in the cafeteria?"

**Expected:** Chatbot returns exact database values with room names ✅

---

## Test Scenario 2 — Campus Information (RAG)
Ask the participant to find:

9. "How do I connect to eduroam WiFi?"
10. "What are the library opening hours?"
11. "What is the after hours helpline number?"
12. "How much does daily parking cost?"
13. "What is the CRICOS code for Master of ICT?"
14. "Who is the course coordinator for Master of ICT?"
15. "What are the rules for having guests in residence?"
16. "How many credit points is the Master of ICT?"

**Expected:** Chatbot returns correct information from PDFs ✅

---

## Test Scenario 3 — Conversational
17. "Hi, what can you help me with?"
18. "Tell me about the campus"
19. "What subjects are in the ICT program?"
20. "How do I apply for the Master of ICT?"

**Expected:** Chatbot responds naturally and helpfully ✅

---

## Observation Checklist (for each participant)
Note during testing:
- [ ] Did the chatbot answer correctly?
- [ ] Was the response time acceptable?
- [ ] Did the participant seem confused?
- [ ] Did the participant need help?
- [ ] Any unexpected errors?
- [ ] Any wrong answers?

---

## Post-Testing
- Ask participant to complete SUS survey (Tarun's link)
- Ask 3 open questions:
  1. "What did you like most about the chatbot?"
  2. "What was most confusing or frustrating?"
  3. "What would you add or improve?"
- Thank participant and record feedback

---

## Known Limitations to Note
- Response time: 1-3 seconds (on-premises)
- Phone numbers: occasionally adds area code prefix
- Server requires SSH tunnel — not publicly accessible yet

---

## Success Criteria
- 10+ students complete testing ✅
- >70% questions answered correctly ✅
- SUS score >70 ✅
- No critical errors during testing ✅