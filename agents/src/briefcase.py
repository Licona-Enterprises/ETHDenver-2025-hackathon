from ica.diana import Diana

if __name__ == "__main__":
    
    diana = Diana()

    listener_process = diana.start_listener()

    while True:
        try:
            diana.api_cool_down()
            if not listener_process.is_alive():
                listener_process = diana.start_listener()

            chroma_db_doc_ids = diana.update_knowledge_base()
    
            diana.start()

            diana.clean_agent_workspace(content=chroma_db_doc_ids)

            diana.api_cool_down()

        except Exception as e:
            print(f"error occured: {e}")
            diana.api_cool_down()