# ExamGPT India

Unified AI-Powered Q&A Platform for Indian Competitive Exams
GATE | CAT | UPSC | IELTS | GRE

## Setup Instructions

1. **Clone the repository** and navigate to `examgpt-india` directory.
2. **Set up the virtual environment:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate # On Mac/Linux
   ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables:**
   - Create a `.env` file in the root directory.
   - Add your Anthropic API key: `ANTHROPIC_API_KEY=sk-ant-your-key-here`
5. **Data Ingestion:**
   ```bash
   python scripts/ingest_pyqs.py
   ```
   This will build the FAISS vector indexes from the sample PYQ data.
6. **Start the Backend server:**
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```
7. **Start the Frontend App:**
   ```bash
   streamlit run frontend/app.py
   ```

## Demo Script for Judges

### Demo Query 1 — Solver (GATE CS)
- **Exam:** GATE — Computer Science
- **Query:** In a system with 3 processes and 4 resource types with instances [3, 2, 1, 2], the Allocation matrix is P0=[1,0,0,0], P1=[0,1,0,1], P2=[1,1,0,0] and Max matrix is P0=[2,1,1,1], P1=[1,1,1,1], P2=[2,2,0,1]. Is the system in a safe state? Find the safe sequence using the Banker's Algorithm.

### Demo Query 2 — Explainer (UPSC)
- **Exam:** UPSC — Civil Services GS
- **Query:** What is the significance of the 73rd Constitutional Amendment Act and how has it affected Panchayati Raj institutions in India?

### Demo Query 3 — Writing Feedback (IELTS)
- **Exam:** IELTS — English Proficiency
- **Query:** Check my essay: Some people think that environmental problems are too big for individuals to solve. Others believe that the government cannot solve these problems without individual effort. Discuss both views and give your opinion. My essay: In todays world environmental problems has become very big. Individual people cannot solve it because they are too small. Government must take action on climate change and pollution. I think government should make more laws. If government make strict rules then environment will become better. Individual effort is also important but government has more power. In conclusion both are important but government must do more.

### Demo Query 4 — Explainer (IELTS Vocab)
- **Exam:** IELTS — English Proficiency
- **Query:** What is the difference between 'affect' and 'effect' and how do I use them correctly in IELTS Writing?
