import os
import dspy
import pandas as pd
from dspy.teleprompt import BootstrapFewShot

# Define the "Signature" for our task.
from dotenv import load_dotenv
from fastmcp.client.transports import StreamableHttpTransport
load_dotenv()
from langchain_sambanova import ChatSambaNovaCloud

from fastmcp import Client as MCPClient
os.environ['SAMBANOVA_API_KEY'] = os.getenv("SAMBANOVA_API_KEY")
sambanova_llm = ChatSambaNovaCloud(
    model="Llama-4-Maverick-17B-128E-Instruct",
    max_tokens=1024,
    temperature=0.1,
    top_p=0.01,
)

dspy.settings.configure(lm=sambanova_llm)
# This tells DSPy what the input and output of our model should be.
class MathSolutionSignature(dspy.Signature):
    """Generate a step-by-step solution to a math question based on provided context."""
    __doc__ = "Generate a step-by-step solution to a math question based on provided context."
    context = dspy.InputField(desc="Relevant information from a knowledge base or web search.")
    question = dspy.InputField(desc="The user's math question.")
    solution = dspy.OutputField(desc="A step-by-step thinking process and the final answer.", prefix="<thinking>")

# Define the DSPy module that will use the signature.
class MathTutor(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_answer = dspy.Predict(MathSolutionSignature)

    def forward(self, question, context):
        return self.generate_answer(question=question, context=context)


def run_optimization():
    """
    Reads feedback, runs the DSPy optimization process, and saves the new prompt.
    """
    feedback_file = "app/feedback.csv"
    optimized_prompt_file = "app/optimized_prompt.json"

    if not os.path.exists(feedback_file):
        print("---OPTIMIZER: No feedback file found. Skipping optimization.---")
        return

    print("---OPTIMIZER: Starting optimization process...---")
    
    # FIX: Removed the dspy.settings.configure() call from this function.
    # The settings are already configured globally in agent.py and will be
    # available to this background thread.

    # Load Feedback Data and create DSPy Examples
    try:
        feedback_df = pd.read_csv(feedback_file)
        if feedback_df.empty or 'question' not in feedback_df.columns or 'correction' not in feedback_df.columns:
            print("---OPTIMIZER: Feedback file is empty or malformed. Skipping.---")
            return
    except Exception as e:
        print(f"---OPTIMIZER: Error reading feedback file: {e}. Skipping.---")
        return
        
    train_set = []
    for index, row in feedback_df.iterrows():
        example = dspy.Example(
            question=str(row['question']),
            context="",
            solution=str(row['correction'])
        ).with_inputs("question", "context")
        train_set.append(example)

    if not train_set:
        print("---OPTIMIZER: No valid training examples created from feedback. Skipping.---")
        return

    print(f"---OPTIMIZER: Loaded {len(train_set)} examples from feedback.---")

    # Set up the Teleprompter for Few-Shot Optimization
    teleprompter = BootstrapFewShot(metric=None, max_bootstrapped_demos=2)
    
    # Compile the program to find the best prompt
    optimized_tutor = teleprompter.compile(MathTutor(), trainset=train_set)

    # Save the optimized program to a file
    optimized_tutor.save(optimized_prompt_file)
    
    print(f"---OPTIMIZER: Optimization complete. New prompt saved to {optimized_prompt_file}---")
