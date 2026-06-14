import pickle
import sys

def inspect_model(filepath):
    try:
        with open(filepath, 'rb') as f:
            model = pickle.load(f)
            print(f"--- Inspecting {filepath} ---")
            print(f"Type: {type(model)}")
            if hasattr(model, 'feature_names_in_'):
                print(f"Features: {model.feature_names_in_}")
            elif hasattr(model, 'classes_'):
                print(f"Classes: {model.classes_}")
            print("\n")
    except Exception as e:
        print(f"Error loading {filepath}: {e}")

if __name__ == "__main__":
    inspect_model(r"d:\amd_tcs_hackathon\Pump_Failure\pump_failure_mode_model.pkl")
    inspect_model(r"d:\amd_tcs_hackathon\Pump_Failure\pump_failure_probability_model.pkl")
    inspect_model(r"d:\amd_tcs_hackathon\Pump_Failure\pump_rul_model.pkl")
    inspect_model(r"d:\amd_tcs_hackathon\Compressor_failure\compressor_failure_mode_model.pkl")
