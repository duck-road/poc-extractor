
def apply_form_processor_to_pdf():
    from google.cloud import storage
    from typing import Sequence
    import os
    from google.api_core.client_options import ClientOptions
    from google.cloud import documentai

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = '../service-account.json'
    project_id = 'aloconcursos-dev'
    location = 'us' # Format is 'us' or 'eu'
    processor_id = '8457a3d172f5073f' # Create processor before running sample
    processor_version = 'rc' # Refer to https://cloud.google.com/document-ai/docs/manage-processor-versions for more information
    file_path = '../raw/BV_SOW_Oportunidades_P_L_v01_63c18accdd_version_8-signed.pdf'
    mime_type = 'application/pdf' # Refer to https://cloud.google.com/document-ai/docs/file-types for supported file types

    def process_document_form_sample(
        project_id: str, location: str, processor_id: str, file_path: str, mime_type: str
    ):
        """
        Process a document with tables and form fields using the Google Document AI API.
        
        This function processes a document and extracts its text, page count, tables, and form fields. It prints
        the extracted information to the console.

        Args:
            project_id (str): The ID of the Google Cloud project.
            location (str): The location of the Document AI processor.
            processor_id (str): The ID of the Document AI processor.
            file_path (str): The path to the input document file.
            mime_type (str): The MIME type of the input document file.
        
        Returns:
            None
        
        Example usage:
            process_document_form_sample(
                "my-project-id",
                "us-central1",
                "my-processor-id",
                "path/to/input/file.pdf",
                "application/pdf"
            )
        """
        document = process_document(
            project_id, location, processor_id, file_path, mime_type
        )
        text = document.text

        # open output.txt file if it exists. Then delete its contents
        open('/tmp/output.txt', 'w').close()

        # Document Header
        header = generate_header("Document Information")
        save_to_file(header)
        save_to_file(f"Full document text: {text}\n")
        save_to_file(f"There are {len(document.pages)} page(s) in this document.")

        for page in document.pages:
            # Page Header
            header = generate_header(f"Page {page.page_number}")
            save_to_file(header)
            
            # Tables Header
            header = generate_header("Tables")
            save_to_file(header)
            save_to_file(f"\nFound {len(page.tables)} table(s):")
            
            for table in page.tables:
                num_collumns = len(table.header_rows[0].cells)
                num_rows = len(table.body_rows)
                
                # Table Header
                header = generate_header(f"Table with {num_collumns} columns and {num_rows} rows")
                save_to_file(header)
                save_to_file("Columns:")
                print_table_rows(table.header_rows, text, save_to_file)
                save_to_file("Table body data:")
                print_table_rows(table.body_rows, text, save_to_file)
            
            # Form Field Header
            header = generate_header("Form Fields")
            save_to_file(header)
            save_to_file(f"\nFound {len(page.form_fields)} form field(s):")
            for field in page.form_fields:
                name = layout_to_text(field.field_name, text)
                value = layout_to_text(field.field_value, text)
                save_to_file(f"    * {name.strip()}: {value.strip()}")

        # save output.txt to bucket gs://poc-extractor/processed/{filename}.txt where filename is the name of the input file
        filename = file_path.split('/')[-1]
        filename = filename.split('.')[0]
        save_to_bucket(bucket_name='poc-extractor', source_file_name='/tmp/output.txt', destination_blob_name=f'processed/{filename}.txt')


    def process_document(
        project_id: str, location: str, processor_id: str, file_path: str, mime_type: str
    ) -> documentai.Document:
        opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
        client = documentai.DocumentProcessorServiceClient(client_options=opts)
        name = client.processor_path(project_id, location, processor_id)
        with open(file_path, "rb") as image:
            image_content = image.read()
        raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)
        result = client.process_document(request=request)
        return result.document

    def print_table_rows(table_rows: Sequence[documentai.Document.Page.Table.TableRow], text: str, save_to_file_func) -> None:
        for table_row in table_rows:
            row_text = ""
            for cell in table_row.cells:
                cell_text = layout_to_text(cell.layout, text)
                row_text += f"{cell_text.strip()} | "
            save_to_file_func(row_text)


    def layout_to_text(layout: documentai.Document.Page.Layout, text: str) -> str:
        """
        Document AI identifies text in different parts of the document by their
        offsets in the entirety of the document's text. This function converts
        offsets to a string.
        """
        response = ""
        for segment in layout.text_anchor.text_segments:
            start_index = int(segment.start_index)
            end_index = int(segment.end_index)
            response += text[start_index:end_index]
        return response


    def save_to_file(text_to_save, filename='/tmp/output.txt'):
        with open(filename, 'a', encoding='utf-8') as f:
            print(text_to_save, file=f)

    def generate_header(title: str, width: int = 150) -> str:
        title = title.upper()
        border = "=" * width
        padding = (width - len(title)) // 2
        title_line = " " * padding + title + " " * padding
        
        if len(title) % 2 != 0:
            title_line = title_line[:-1]
        
        return f'''
{border}
{title_line}
{border}
'''

    def save_to_bucket(bucket_name, source_file_name, destination_blob_name):
        """Uploads a file to the bucket."""
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.content_type = "text/plain"
        blob.content_encoding = "utf-8"

        with open(source_file_name, "rb") as f:
            blob.upload_from_file(f)


    process_document_form_sample(project_id, location, processor_id, file_path, mime_type)

if __name__ == "__main__":
    apply_form_processor_to_pdf()
