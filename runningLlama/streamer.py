from datetime import datetime

class TimeLoggingStreamer:
    """
    Initializes the tokenizer with the provided tokenizer and sets up
    empty lists to hold tokens and their corresponding timestamps.

    Args:
        tokenizer (Tokenizer): The tokenizer that will be used to decode
                                the model's outputs. It is responsible for 
                                converting tokens back into human-readable text.

    Attributes:
        tokenizer (Tokenizer): The tokenizer passed in during initialization.
        tokens (list): A list that will store the tokens as they are processed.
        timestamps (list): A list that will store timestamps corresponding to 
                            the tokens as they are processed.
    """
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.tokens = []
        self.timestamps = []
    
    
    def getTimesStamps(self):
        """
        Retireves all of the associated timestamps with each
        token being produced
        """
        return self.timestamps
    
    def put(self, token_ids):
        """
        The put function is called by the model everytime a token
        is created. It then uses the tokens_ids to map to decoded text.
        It also created associates a time for everytime a token is created.

        Args:
            token_ids: holds the tokens created by the model
        
        """
        # take time
        now = datetime.now()

        # reshape token id
        token_ids = token_ids.tolist()

        # adds the tokens id to existing tokens
        self.tokens.extend(token_ids)

        # adds the associated times
        self.timestamps.append(now) 

        # decodes last provided token_id
        decoded_text = self.tokenizer.decode(token_ids[-1], skip_special_tokens=True)
        print(decoded_text, end='', flush=True)

    def end(self):
        """
        Called when streaming ends.
        """
        print("\nGeneration complete.")