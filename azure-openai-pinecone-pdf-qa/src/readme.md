# Azure OpenAI, Pinecone, Chainlit, LangChain, PDF Processing, Question Answering


This repository contains a Chainlit application that provides a question-answering service using documents stored in a Pinecone vector store. It allows users to upload PDF documents, which are then chunked, embedded using Azure Open AI service, and indexed for efficient retrieval. When a user asks a question, the application retrieves relevant document chunks and uses Azure OpenAI's language model to generate an answer.

## High Level Description

The app.py script performs the following functions:

- PDF Processing (process_pdfs): Chunks PDF files into smaller text segments.
- Creates embeddings for each chunk using Azure Open AI service, and stores them in Pinecone.
- Question Answering (on_message): When a user asks a question, the application retrieves relevant document chunks and generates an answer using Azure OpenAI's language model, providing the sources for transparency.

The following files are also included in the repository:
- requirements.txt: Lists the required Python packages.
- Dockerfile: Used to build a Docker image for the application.
- .env: Contains the environment variables.
- build-docker-image.sh: A script to build the Docker image.
- run-docker-image.sh: A script to run the Docker image locally.
- push-docker-image.sh: A script to push the Docker image to an Azure Container Registry
- variables.sh: contains the variables for the Azure Container Registry, and the Docker image.

## Quickstart

### Prerequisites:
- An active [Azure Subscription](https://learn.microsoft.com/en-us/azure/guides/developer/azure-developer-guide#understanding-accounts-subscriptions-and-billing). If you don't have one, create a [free Azure account](https://azure.microsoft.com/en-gb/free/) before you begin.
- [VS Code](https://code.visualstudio.com/) as a code editor.
- [Docker](https://www.docker.com/) installed on your local machine.
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed on your local machine.
- [Pinecone account](https://www.pinecone.io/) and API key.
- [Azure OpenAI account](https://azure.microsoft.com/en-us/services/cognitive-services/openai/). You will need to create a resource and obtain your OpenAI Endpoint, API Key, deploy text-embedding-ada-002 and gpt-35-turbo-16k model.
- Pdf document to be uploaded in the folder `pdfs`. This document will be indexed and used for question answering.
- Python 3.11 or higher installed on your local machine.
- (Optional) [Azure Container Registry](https://docs.microsoft.com/en-us/azure/container-registry/) to store the Docker image. This step is optional, if you want to deploy the application to Azure Container Apps for example.

### Setup the environment variables

1. Create an .env file and update the following environment variables:

    ```
    AZURE_OPENAI_API_KEY=d49e7825c734484b86c6803d4452ce68 
    # replace with your Azure OpenAI API Key

    AZURE_OPENAI_ENDPOINT=https://pineconellmdemoopenai.openai.azure.com/ 
    # replace with your Azure OpenAI Endpoint

    AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-35-turbo-16k
    #Create a deployment for the gpt-35-turbo-16k model and place the deployment name here. You can name the deployment as per your choice and put the name here. #In my case, I have named it as `gpt-35-turbo-16k`.

    AZURE_OPENAI_CHAT_DEPLOYMENT_VERSION=2023-07-01-preview 
    #You don't need to change this unless you are willing to try other versions.

    PINECONE_API_KEY=a592424f-ba4e-4c66-a0d2-deda1dcd1de9 
    #Change this to your Pinecone API Key

    AZURE_OPENAI_ADA_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002 
    #Create a new deployment in the Azure Open AI Studio using the text-embedding-ada-002 #model and place the deployment name here. You can name the deployment #as per your #choice and put the name here. In my case, I have named it as `text-embedding-ada-002`.

    AZURE_OPENAI_ADA_EMBEDDING_MODEL_NAME=text-embedding-ada-002 
    #This is the model name of the text-embedding-ada-002 deployment model from above. You don't need to change it as it will be the same in your case.

    AZURE_OPENAI_ADA_DEPLOYMENT_VERSION=2024-02-15-preview
    #You don't need to change this unless you are willing to try earlier versions.
    ```

Once you have updated the .env file, please save the changes and you are ready to proceed to the next step.

### Option 1: Run the application locally

1. Install dependencies: 
Open the terminal and navigate to the src folder of the repository. Then run the following command to install the necesairly Python packages:

    ```pip
    pip install -r requirements.txt
    ```

2. Process pdf files: In the folder 'pdfs', place the pdf document that you want to use for answering questions.

3. Run the application: Run the following command to start the application:

    ```chainlit
     chainlit run app.py -w
    ```
4. Test the application: Open a new terminal and run the following command to test the application:

    ```chainlit
     http://localhost:8000/
    ```
    You can now upload a pdf document and ask questions to test the application.

![Screen](src/images/Screenshot 2024-02-18 at 16.58.21.png)

### Option 2: Run the application in a Docker container

1. Navigate to the src folder of the repository

2. Open the file build-docker-image.sh and depending on the architecture of your local machine (linux/arm64 or linux/amd64), uncomment the respective line and comment the other line. Then save the file. In my case I built the image to run it locally on my M1 Mac, so I have uncommented the line for linux/arm64 and commented the line for linux/amd64. If you plan to build the image for a different architecture, you can uncomment the respective line and comment the other line.

3. Run the following command to build the Docker image:

    ```build-docker-image
     ./build-docker-image.sh
    ```
4. Run the following command to run the Docker image:

    ```run-docker-image
     ./run-docker-image.sh
    ```
5. Test the application: Open a new terminal and run the following command to test the application:

    ```chainlit
     http://localhost:8000/
    ```
![Screen](src/images/Screenshot 2024-02-18 at 17.13.36.png)

6. (optional) Push the Docker image to an Azure Container Registry

    If you want to deploy the application to Azure, you can push the Docker image to an Azure Container Registry. To do this, you need to have an Azure Container Registry and the Docker image name and the Azure Container Registry name in the variables.sh file. Once you have updated the variables.sh file, run the following Azure CLI command to connect to your Azure Subscription:
    
    ```azure
    az login
    ```

    Then run the following command to push the Docker image to the Azure Container Registry:

    ```push-docker-image
    ./push-docker-image.sh
    ```