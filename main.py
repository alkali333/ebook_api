from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from functions import create_chapters, write_next_chapter, summarize
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class EbookInput(BaseModel):
    title: str
    description: Optional[str] = None
    number_of_chapters: int
    words_per_chapter: int
    model: str = "gpt-3.5-turbo"
    api_key: Optional[str] = None


@app.post("/create_ebook")
async def create_ebook(ebook: EbookInput):
    chapter_list = []
    ebook_content = ""
    summary_so_far = ""

    try:
        response_list = create_chapters(
            number=ebook.number_of_chapters,
            title=ebook.title,
            description=ebook.description,
            model=ebook.model,
            api_key=ebook.api_key,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    for field in response_list:
        chapter_list.append(field.strip())

    for i, chapter in enumerate(chapter_list):
        ebook_content += f"<h1>Chapter {i+1}: {chapter}</h2> \n\n"

        try:
            response = write_next_chapter(
                book_name=ebook.title,
                book_description=ebook.description,
                chapter_number=i + 1,
                chapter_name=chapter_list[i],
                summary_so_far=summary_so_far,
                number_of_words=ebook.words_per_chapter,
                model=ebook.model,
                api_key=ebook.api_key,
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

        ebook_content += response.replace("\n", "</p><p>")
        ebook_content = "<p>" + ebook_content + "</p><br/><br/><br/>"

        summary_length = max(min(round(ebook.words_per_chapter / 7), 100), 50)
        try:
            summary = summarize(
                input=response,
                number_of_words=summary_length,
                model=ebook.model,
                api_key=ebook.api_key,
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

        if len(summary_so_far.split()) > 1200:
            try:
                summary = summarize(
                    input=summary_so_far,
                    number_of_words=600,
                    model=ebook.model,
                    api_key=ebook.api_key,
                )
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        summary_so_far += f"Chapter {i+1} Summary: {summary} \n\n"

    return {"ebook_content": ebook_content}
