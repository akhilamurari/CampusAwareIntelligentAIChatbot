# CampusAware AI — Sprint 5 Usability Report
## Cisco-La Trobe University AI & IoT Centre
### Prepared by: Harshitha Kolipaka
### Reviewed by: Akhila Murari
### Date: April 2026

---

## 1. Executive Summary

The CampusAware Intelligent AI Chatbot was developed as a digital twin assistant for La Trobe University's Bundoora campus. Sprint 5 focused on user testing, usability evaluation and knowledge base expansion.

**Key Findings:**
- SUS Score: **87/100 (Excellent)** — exceeds target of 70
- Overall Rating: **10/10 respondents rated Excellent ⭐⭐⭐⭐⭐**
- NL2SQL Accuracy: **100%**
- RAG Document Accuracy: **100%**
- Average Response Time: **1.8 seconds**

---

## 2. System Overview

| Component | Details |
|---|---|
| Model | Qwen2.5-7B-Instruct (on-premises) |
| Server | aiotcentre-03 (4x NVIDIA L40S GPUs, 46GB each) |
| Framework | LangGraph + LangChain + vLLM |
| Database | SQLite (48,960 IoT records, 17 rooms) |
| Knowledge Base | FAISS vector store (246 chunks, 10 PDFs) |
| Interface | Streamlit web application |
| Public Access | ngrok tunnel |

---

## 3. User Testing

### 3.1 Testing Overview
- **Total Respondents:** 10
- **Testing Date:** 28 April 2026
- **Testing Method:** Google Form with live chatbot access
- **Chatbot URL:** https://glorify-overcome-provoke.ngrok-free.dev
- **Duration per session:** 15-20 minutes

### 3.2 Participant Demographics

| Name | La Trobe Student | Study Level |
|---|---|---|
| Akhila | Yes | Postgraduate |
| Dillep | No | Other |
| Krishna | Yes | Undergraduate |
| Kaundinya | No | Other |
| Jayaansh | No | Undergraduate |
| Ritika | No | Other |
| Karthik | No | Postgraduate |
| Lahari | Yes | Postgraduate |
| Sukesh | No | Other |
| Surya | No | Other |

- **La Trobe students:** 4 (40%)
- **Non-La Trobe:** 6 (60%)
- **Postgraduate:** 3 (30%)
- **Undergraduate:** 2 (20%)
- **Other:** 5 (50%)

---

## 4. Query Accuracy Ratings

Respondents tested the chatbot with specific queries and rated accuracy on a 1-5 scale.

### 4.1 NL2SQL Query Ratings

| Query | Individual Scores | Average |
|---|---|---|
| "Which room had the highest CO2 levels?" | 5,5,5,5,5,5,5,5,5,5 | **5.0/5** ✅ |
| "Find me a quiet room to study" | 5,5,5,5,5,5,5,5,5,5 | **5.0/5** ✅ |

### 4.2 RAG Query Ratings

| Query | Individual Scores | Average |
|---|---|---|
| "How do I connect to eduroam WiFi?" | 5,5,4,5,5,5,5,5,5,5 | **4.9/5** ✅ |

### 4.3 Overall Rating

| Rating | Count | Percentage |
|---|---|---|
| ⭐⭐⭐⭐⭐ Excellent | 10 | 100% |
| ⭐⭐⭐⭐ Very Good | 0 | 0% |
| ⭐⭐⭐ Good | 0 | 0% |

**10/10 respondents rated the chatbot as Excellent** 🎉

---

## 5. System Usability Scale (SUS) Analysis

### 5.1 About SUS
The System Usability Scale (SUS) is a standardised usability measurement tool. Standard SUS uses 10 questions. This evaluation used 5 adapted SUS questions on a 1-5 Likert scale.

### 5.2 SUS Questions Used

| # | Question | Type |
|---|---|---|
| Q1 | I think that I would like to use this system frequently | Positive |
| Q2 | I found the system unnecessarily complex | Negative |
| Q3 | I thought the system was easy to use | Positive |
| Q4 | I think that I would need the support of a technical person to use this system | Negative |
| Q5 | I found the various functions in this system were well integrated | Positive |

### 5.3 SUS Calculation Method

**Formula:**
- Positive questions (Q1, Q3, Q5): contribution = score - 1
- Negative questions (Q2, Q4): contribution = 5 - score
- SUS Score = Sum of all contributions × 5

**Maximum possible score = 20 × 5 = 100**

### 5.4 Raw Responses and Calculations

| Respondent | Q1 | Q2 | Q3 | Q4 | Q5 | Calc | Score |
|---|---|---|---|---|---|---|---|
| Akhila | 5 | 1 | 5 | 1 | 5 | (4)+(4)+(4)+(4)+(4)=20 | **100** |
| Dillep | 5 | 1 | 5 | 1 | 5 | (4)+(4)+(4)+(4)+(4)=20 | **100** |
| Krishna | 5 | 1 | 5 | 1 | 5 | (4)+(4)+(4)+(4)+(4)=20 | **100** |
| Kaundinya | 5 | 1 | 5 | 5 | 5 | (4)+(4)+(4)+(0)+(4)=16 | **80** |
| Jayaansh | 5 | 1 | 5 | 5 | 5 | (4)+(4)+(4)+(0)+(4)=16 | **80** |
| Ritika | 5 | 2 | 5 | 1 | 5 | (4)+(3)+(4)+(4)+(4)=19 | **95** |
| Karthik | 5 | 2 | 5 | 5 | 5 | (4)+(3)+(4)+(0)+(4)=15 | **75** |
| Lahari | 5 | 1 | 5 | 5 | 5 | (4)+(4)+(4)+(0)+(4)=16 | **80** |
| Sukesh | 5 | 1 | 5 | 5 | 5 | (4)+(4)+(4)+(0)+(4)=16 | **80** |
| Surya | 5 | 1 | 5 | 5 | 5 | (4)+(4)+(4)+(0)+(4)=16 | **80** |
| **Total** | | | | | | **174** | **870** |
| **Average** | | | | | | **17.4** | **87.0** |

**Average SUS Score = 870 ÷ 10 = 87/100**

### 5.5 SUS Score Interpretation

| Score Range | Grade | Adjective |
|---|---|---|
| 90 - 100 | A | Best Imaginable |
| **80 - 89** | **B** | **Excellent ← Our Score (87)** |
| 70 - 79 | C | Good |
| 60 - 69 | D | OK |
| 51 - 59 | E | Poor |
| < 51 | F | Awful |

**Our score of 87 = Excellent (Grade B)** ✅
**Target was >70 — exceeded by 17 points** 🎉

### 5.6 Individual Score Distribution

| Score Range | Count | Respondents |
|---|---|---|
| 95-100 | 4 | Akhila, Dillep, Krishna, Ritika |
| 80-94 | 5 | Kaundinya, Jayaansh, Lahari, Sukesh, Surya |
| 75-79 | 1 | Karthik |

---

## 6. Technical Accuracy Evaluation

### 6.1 RAG Document Retrieval Accuracy

| Query | Expected Answer | Chatbot Answer | Result |
|---|---|---|---|
| After hours helpline | 1800 758 360 | 1800 758 360 | ✅ |
| Campus security | 9479 2222 | 9479 2222 | ✅ |
| Security escort | 9479 2012 | 9479 2012 | ✅ |
| CRICOS code Master ICT | 061684F | 061684F | ✅ |
| Course coordinator | Lydia Cui | Lydia Cui | ✅ |
| Credit points | 195 | 195 | ✅ |
| ICT duration full time | 2 years | 2 years | ✅ |
| White bay parking | $8.45 daily max | $8.45 daily max | ✅ |
| Free bus name | The Glider | The Glider | ✅ |
| Guest rules | Max 1 night/4 weeks | Max 1 night/4 weeks | ✅ |
| eduroam WiFi | Step by step guide | Step by step guide | ✅ |

**RAG Accuracy: 11/11 = 100%** ✅

### 6.2 NL2SQL Database Query Accuracy

| Query | Expected | Result |
|---|---|---|
| Highest CO2 room | Library-L3 (1322.33 ppm) | ✅ |
| Quietest study room | Study-Room with lowest dB | ✅ |
| Average library temperature | ~22-24°C | ✅ |
| Currently occupied rooms | Full room list | ✅ |
| Cafeteria noise level | Exact dB value | ✅ |
| Best air quality room | Room name + air quality | ✅ |
| Room humidity | Exact % value | ✅ |
| Lecture hall availability | Occupancy status | ✅ |

**NL2SQL Accuracy: 8/8 = 100%** ✅

### 6.3 Automated Test Results

```
✅ test_agent_nl2sql_connection    PASSED
✅ test_agent_rag_retrieval        PASSED
✅ test_agent_rag_retrieval_specifically PASSED
✅ test_agent_multi_turn           PASSED
4 passed in 24.62s
```

---

## 7. Performance Metrics

| Metric | Value |
|---|---|
| Average response time | 1.8 seconds |
| Fastest response | 0.4 seconds |
| Slowest response | 3.3 seconds |
| Cloud API response time | 41.7 seconds |
| Speed improvement | **23x faster on-premises** |
| GPU used | GPU 1 — NVIDIA L40S (46GB) |
| Model size | 15GB |
| Database records | 48,960 |
| IoT rooms monitored | 17 |
| Knowledge base chunks | 246 |
| Knowledge base PDFs | 10 |

---

## 8. User Feedback

### 8.1 What Users Liked
- *"Chatbot interface and response time is good"*
- *"Accuracy of answers, easy to use"*
- *"Features they found useful — room sensors, policy info, campus map"*
- *"Easy to use. UX could be improved"*
- *"Very Good tool to know about La Trobe University"*
- *"It is designed to provide accurate and helpful information quickly"*
- *"Easy to use"*
- *"Happy to use all the features in one place"*
- *"I loved it, easy to use"*
- *"Good to see the concept and UI is good"*

### 8.2 Key Themes from Feedback
1. **Ease of use** — consistently mentioned across all respondents
2. **Response speed** — appreciated by multiple users
3. **Information accuracy** — highly rated
4. **UI/UX** — good but room for improvement

---

## 9. Known Limitations

| Limitation | Severity | Proposed Resolution |
|---|---|---|
| SSH tunnel required for connection | Medium | Ansu's server stability work (CF1CT-34) |
| LLaMA 70B access pending Meta approval | Low | Monitor HuggingFace approval |
| ngrok URL changes on restart | Low | Upgrade ngrok or deploy permanently |
| Complex policy question accuracy | Low | Larger model or fine-tuning |
| Single GPU deployment | Low | Multi-GPU for production scaling |

---

## 10. Sprint 5 Completion Summary

| Ticket | Task | Assignee | Status |
|---|---|---|---|
| CF1CT-29 | User Testing (10+ students) | Akhila | ✅ DONE |
| CF1CT-30 | SUS Survey Design & Analysis | Tarun | ✅ DONE |
| CF1CT-31 | RAGAS Evaluation | Jince | ✅ DONE |
| CF1CT-32 | Usability Report | Harshitha | ✅ DONE |
| CF1CT-33 | Expand PDF Knowledge Base | Bennet | ✅ DONE |
| CF1CT-34 | Server Stability & Auto-restart | Ansu | ✅ DONE |

---

## 11. Future Recommendations

1. **Upgrade to LLaMA 70B** — Once Meta approves HuggingFace access, deploy LLaMA 3.1 70B for improved complex query accuracy

2. **Permanent server deployment** — Configure vLLM to auto-start on server boot, eliminating manual SSH sessions

3. **Mobile application** — Develop iOS and Android versions for on-campus student use

4. **Room booking integration** — Allow students to reserve available rooms directly via chatbot

5. **Extended campus data** — Integrate timetables, canteen menus, event schedules and bus real-time tracking

6. **Multi-language support** — Add support for international students in their native languages

7. **Voice interface** — Implement speech-to-text for hands-free campus navigation

8. **Fine-tuning** — Fine-tune Qwen2.5-7B on La Trobe specific data for improved policy question accuracy

---

## 12. Conclusion

The CampusAware AI chatbot has successfully achieved all Sprint 5 objectives. The system demonstrates:

- **Excellent usability** — SUS score 87/100, exceeding the 70 target
- **Perfect accuracy** — 100% NL2SQL and 100% RAG for key campus information
- **Fast responses** — 1.8 seconds average (23x faster than cloud API)
- **Universal approval** — 10/10 respondents rated Excellent

The chatbot is ready for the Sprint 6 stakeholder demonstration to Scott Mayfield, Phu Lai and Dr Di Wu. This project represents a significant achievement in on-premises AI deployment for La Trobe University's Bundoora campus digital twin initiative.

---

*Report prepared for: Dr Di Wu, Phu Lai, Scott Mayfield*
*Project: Cisco-La Trobe CampusAware Intelligent AI Chatbot*
*Team: Akhila Murari, Tarun, Harshitha Kolipaka, Bennet, Jince, Ansu*
*Supervisors: Dr Di Wu, Phu Lai*
*GitHub: github.com/akhilamurari/CampusAwareIntelligentAIChatbot*