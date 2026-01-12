from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, Response
from app.utils.generate_resume import build_resume_model
from app.utils.generate_resume_tex import generate_resume_tex
import subprocess
import tempfile
import os

router = APIRouter()

@router.get("/resume", response_class=HTMLResponse)
def resume_page():
    resume_model = build_resume_model()
    tex = generate_resume_tex(resume_model)
    preview = tex.replace("<", "&lt;").replace(">", "&gt;")
    return (
        """
        <html>
            <body style="font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">
                <h2>Resume Export</h2>
                <p>Download your LaTeX/PDF resume:</p>
                <p><a href="/resume/download">Download resume.tex</a></p>
                <p><a href="/resume/pdf">Download resume.pdf</a></p>
                <h3>Preview (LaTeX)</h3>
                <pre style="white-space: pre-wrap; border:1px solid #ddd; padding:10px; max-height: 50vh; overflow:auto; background:#fafafa;">"""
        + preview
        + """</pre>
            </body>
        </html>
        """
    )

@router.get("/resume/download")
def resume_download():
    resume_model = build_resume_model()
    tex = generate_resume_tex(resume_model)
    return Response(
        content=tex,
        media_type="application/x-tex",
        headers={"Content-Disposition": "attachment; filename=resume.tex"},
    )

def compile_pdf(tex: str) -> bytes:
    """
    Compile LaTeX source to PDF using pdflatex (single pass).

    Raises HTTPException with LaTeX logs on failure.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        basename = "resume"
        tex_path = os.path.join(tmpdir, f"{basename}.tex")
        pdf_path = os.path.join(tmpdir, f"{basename}.pdf")

        # Write LaTeX source
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(tex)

        try:
            proc = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", f"{basename}.tex"],
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
            )

            # If pdflatex exited non-zero AND no PDF exists → fail
            if proc.returncode != 0 and not os.path.exists(pdf_path):
                raise subprocess.CalledProcessError(
                    proc.returncode,
                    proc.args,
                    output=proc.stdout,
                    stderr=proc.stderr,
                )

        except subprocess.TimeoutExpired:
            raise HTTPException(
                status_code=500,
                detail="LaTeX compilation timed out.",
            )

        except FileNotFoundError:
            raise HTTPException(
                status_code=500,
                detail="pdflatex not found. Is LaTeX installed in the container?",
            )

        except subprocess.CalledProcessError as e:
            raise HTTPException(
                status_code=500,
                detail=(
                    "LaTeX compilation failed.\n\n"
                    f"STDOUT:\n{(e.output or b'').decode(errors='ignore')[-1500:]}\n\n"
                    f"STDERR:\n{(e.stderr or b'').decode(errors='ignore')[-1500:]}"
                ),
            )

        if not os.path.exists(pdf_path):
            raise HTTPException(
                status_code=500,
                detail="PDF was not generated. LaTeX likely failed.",
            )

        with open(pdf_path, "rb") as f:
            return f.read()
        
@router.get("/resume/pdf")
def resume_pdf():
    resume_model = build_resume_model()
    tex = generate_resume_tex(resume_model)
    pdf_bytes = compile_pdf(tex)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=resume.pdf"},
    )