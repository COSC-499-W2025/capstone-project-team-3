
 # System Architecture Diagram
 ![System Architecture Diagram](../screenshots/System_Architecture_updated.png)
 [View full‑size diagram as PDF](System_Architecture_updated.pdf)

 _Note: Diagram is shown in the PDF for a clearer, high‑resolution view._

 ## Description of the diagram
The system architecture is organized into three layers: the User Interface layer, the Core Processing layer, and the Data Storage layer. Together, these layers support the end-to-end workflow of transforming a user’s raw project data into structured, customizable portfolio and résumé outputs.

## 1. User Interface Layer

The entry point for all user interactions, built as a **Desktop Application**.

- **Security & Consent:** A "hard gate" consent mechanism ensures no data analysis occurs without explicit user authorization.
- **Data Ingestion:** Users upload project ZIP files directly into the UI for processing.
- **Visualization:** The **Portfolio UI** and **Resume** views render the final analysis, scores, and generated metrics.
