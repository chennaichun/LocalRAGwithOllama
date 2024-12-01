import streamlit as st
import pandas as pd
import chromadb
import ollama  # Ensure that ollama is correctly installed and imported

# Define an initialization function to set up the Streamlit session state
def initialize():
    # Use the get method to set a default value to avoid AttributeError
    if st.session_state.get("already_executed", False) == False:
        setup_database()  # Call the setup_database function to configure the database and load data
        st.session_state.already_executed = True  # Set to True after initialization

# Define the function to set up the database
def setup_database():
    client = chromadb.Client()  # Create a chromadb client for interacting with the database
    file_path = '/Users/data/Arch_QA.xlsx'  # Specify the path and name of the Excel file
    documents = pd.read_excel(file_path, header=None)  # Read the Excel file using pandas

    # Use the chromadb client to create or get a collection named 'demodocs'
    collection = client.get_or_create_collection(name="demodocs")

    # Iterate over the data read from the Excel file, where each row represents a record
    for index, content in documents.iterrows():
        response = ollama.embeddings(model="mxbai-embed-large", prompt=content[0])  # Generate embeddings for the text in the row using ollama
        collection.add(ids=[str(index)], embeddings=[response["embedding"]], documents=[content[0]])  # Add the text and its embeddings to the collection

    st.session_state.collection = collection  # Save the collection in the session state for later use    

# Define a function to create a new chromadb client, establishing a new connection each time
def create_chromadb_client():
    return chromadb.Client()  # Return a new chromadb client instance

# Main function to build the UI and handle user events
def main():
    initialize()  # Call the initialization function
    st.title("Local LLM+RAG")  # Set the title in the web application
    user_input = st.text_area("What would you like to ask?", "")  # Create a text area for user input

    # If the user clicks the "Submit" button
    if st.button("Submit"):
        if user_input:
            handle_user_input(user_input, st.session_state.collection)  # Process user input, perform query, and generate response
        else:
            st.warning("Please enter a question!")  # Show a warning message if no input is provided

# Define the function to handle user input
def handle_user_input(user_input, collection):
    response = ollama.embeddings(prompt=user_input, model="mxbai-embed-large")  # Generate embeddings for user input
    results = collection.query(query_embeddings=[response["embedding"]], n_results=3)  # Query the collection for the top 3 most relevant documents
    data = results['documents'][0]  # Retrieve the most relevant document
    output = ollama.generate(
        model="llama3.1:latest",
        #model="ycchen/breeze-7b-instruct-v1_0",
        prompt=f"Using this data: {data}. Respond to this prompt and use Chinese: {user_input}"  # Generate a response
    )
    st.text("Answer:")  # Display "Answer:"
    st.write(output['response'])  # Display the generated response on the webpage

if __name__ == "__main__":
    main()  # If this file is executed directly, run the main function
