
def apply_form_processor_to_pdf():
    from typing import Sequence
    import os
    from google.api_core.client_options import ClientOptions
    from google.cloud import documentai

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = '../service-account.json'
    project_id = 'aloconcursos-dev'
    location = 'us' # Format is 'us' or 'eu'
    processor_id = '8457a3d172f5073f' # Create processor before running sample
    processor_version = 'rc' # Refer to https://cloud.google.com/document-ai/docs/manage-processor-versions for more information
    file_path = '../raw/C-536-Contrato_de_Prestacao_de_Servicos_20092017/C-536-AD1-1_Aditivo_ao_Contrato_de_Prestac_a_o_de_Servic_os.pdf'
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

        print(f"Full document text: {repr(text)}\n")
        print(f"There are {len(document.pages)} page(s) in this document.")
        for page in document.pages:
            print(f"\n\n**** Page {page.page_number} ****")
            print(f"\nFound {len(page.tables)} table(s):")
            for table in page.tables:
                num_collumns = len(table.header_rows[0].cells)
                num_rows = len(table.body_rows)
                print(f"Table with {num_collumns} columns and {num_rows} rows:")
                print("Columns:")
                print_table_rows(table.header_rows, text)
                print("Table body data:")
                print_table_rows(table.body_rows, text)
            print(f"\nFound {len(page.form_fields)} form field(s):")
            for field in page.form_fields:
                name = layout_to_text(field.field_name, text)
                value = layout_to_text(field.field_value, text)
                print(f"    * {repr(name.strip())}: {repr(value.strip())}")

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

    def print_table_rows(
        table_rows: Sequence[documentai.Document.Page.Table.TableRow], text: str
    ) -> None:
        for table_row in table_rows:
            row_text = ""
            for cell in table_row.cells:
                cell_text = layout_to_text(cell.layout, text)
                row_text += f"{repr(cell_text.strip())} | "
            print(row_text)

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
    process_document_form_sample(project_id, location, processor_id, file_path, mime_type)

if __name__ == "__main__":
    apply_form_processor_to_pdf()
