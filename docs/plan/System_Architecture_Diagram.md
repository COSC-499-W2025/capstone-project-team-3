
 # System Architecture Diagram
 ![System Architecture Diagram](../screenshots/System%20Architecture%20Final.png)
 [View full‑size diagram as PDF](System%20Architecture%20Final.pdf)

 _Note: Diagram is shown in the PDF for a clearer, high‑resolution view._

## Description of the diagram

The system architecture is organized into three layers: the User Interface layer, the Core Processing layer, and the Data Storage layer. Together, these layers enable a complete workflow, from secure data ingestion to advanced analysis, personalization, and export of professional assets such as portfolios, résumés, and cover letters.

---

## 1. User Interface Layer

The entry point for all user interactions, built as a **Desktop Application**.

### **Consent & Security**

* A **Consent Form** acts as a hard gate, ensuring explicit user authorization before any data processing begins.
* Additional consent is required for **external services (AI usage)**.

### **Core Application Interface**

* The **Desktop Application** orchestrates all UI interactions and communicates with backend services.
* Includes centralized **error handling** via an *Alert User* mechanism.

### **User-Facing Features**

* **Portfolio UI**: Displays analyzed project insights, scores, and visual metrics.

* **Resume UI**: Generates and presents structured résumé outputs.

* **Cover Letter UI**: Enables AI-assisted or local generation of tailored cover letters.

* **Job Match Interface**: Allows users to compare their résumé against job descriptions through AI or local comparison.

* **Learnings Page**: Provides insights and recommendations derived from analyzed data.

* **Data Management UI**: Lets users manage projects, configurations, and stored data.

* UI components interact with stored analysis data and support exporting generated outputs.

* The **Cover Letter UI** can trigger analysis mode selection for content generation.

* The Desktop Application also interfaces with the **Local File System** for handling uploads and local assets.

---

## 2. Core Processing Layer (FastAPI Backend)

The "engine" of the system, orchestrated by a **FastAPI** backend that manages data transformation and analysis logic.

* **Pre-Processing:**
  Raw uploads are handled by a **Decompress Engine** and **File Scanner**. Each project is assigned a unique signature to prevent redundant analysis and ensure data integrity. A **Metadata Extractor** processes project-level information, while **Personal Info Collection** captures user data used for personalization. **User Config Storage** maintains user preferences and consent states, and an **External Services Consent** step ensures approval before invoking AI-related functionality.

* **Dual-Track Pipeline:**

  * **Code Pipeline:** Analyzes source files and utilizes a **Git Analysis Engine** to extract repository-level signals and contribution data.
  * **Non-Code Pipeline:** Parses documentation and project metadata to classify individual versus collaborative contributions through a **Content Parser**.

* **Hybrid Analysis Mode:**
  The system features an **Analysis Choice** logic. It can operate in **Local-only** mode for maximum privacy using a **Content Analyzer**, or **AI-enhanced** mode (via **Gemini**) using an **AI Generator** to generate enriched resume bullets, cover letters, and professional summaries.

* **Additional Processing:**

  * A **Job Matching Engine** evaluates alignment between résumés and job descriptions.
  * A **Learning Insights Engine** generates insights and recommendations based on analyzed data.
  * A **Project Management Service** handles project-level operations and coordination with storage.

* **The Merger:**
  Final outputs from both pipelines and the selected analysis mode are synthesized into a unified **Merged Analysis**, including skills, scores, dashboard metrics, and generated content used across résumé, portfolio, and cover letter features.

* Errors occurring during processing are propagated back to the UI through the *Alert User* mechanism.

---

## 3. Data Storage Layer

Ensures persistence and provides the source of truth for the application state.

* **Metadata & Analysis:**
  An **SQLite** database stores user configurations, consent logs, project metadata, generated metrics, merged analysis results, job matching outputs, and learning insights.

* **File Persistence:**
  The **Local File System** manages raw uploads, thumbnails, and temporary processing artifacts, and is directly accessed by the Desktop Application.

* **Export Engine:**
  Finalized results are funneled into **Export Storage**, allowing users to download their professional assets in **TeX** or **PDF** formats for résumés, **HTML** for portfolios, and **PDF** cover letters.

* UI components such as Portfolio, Resume, and Cover Letter interfaces read from and write to the database.

* Analysis components write results directly to persistent storage, enabling reuse across features like job matching and learning insights.
