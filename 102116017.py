import sys
import numpy as np
import pandas as pd


def read_data(input_file):
    try:
        data = pd.read_csv(input_file)
        return data
    except FileNotFoundError:
        print("Error: File not found.")
        return None


def parse_weights_and_impacts(weights, impacts):
    try:
        weights_array = np.fromiter(
            map(float, weights.split(',')), dtype=float)
        symbols = impacts.split(',')
        symbol_to_number = {'+': 1, '-': -1}
        numbers = [symbol_to_number[symbol.strip()] for symbol in symbols]
        impacts_array = np.array(numbers)
        return weights_array, impacts_array
    except ValueError as e:
        print(f"Error parsing weights and impacts: {e}")
        return None, None


def check_columns(data):
    try:
        return len(data.iloc[0]) >= 3
    except Exception as e:
        print(f"Error checking columns: {e}")
        return False


def normalize_data(data):
    numerical_values = data.iloc[:, 1:].values.tolist()
    numerical_values_np = np.array(numerical_values)
    normalized_matrix = numerical_values_np / \
        np.sqrt((numerical_values_np ** 2).sum(axis=0))
    return normalized_matrix


def perform_topsis(normalized_data, weights, impacts):
    weighted_matrix = normalized_data * weights * impacts

    ideal_solution = np.abs(np.array([weighted_matrix[:, i].max(
    ) if weights[i] > 0 else weighted_matrix[:, i].min() for i in range(len(weights))]))
    negative_ideal_solution = np.abs(np.array([weighted_matrix[:, i].min(
    ) if weights[i] > 0 else weighted_matrix[:, i].max() for i in range(len(weights))]))

    weighted_matrix = np.abs(weighted_matrix)

    euclidean_distance_ideal = np.sqrt(
        ((weighted_matrix - ideal_solution) ** 2).sum(axis=1))
    euclidean_distance_negative_ideal = np.sqrt(
        ((weighted_matrix - negative_ideal_solution) ** 2).sum(axis=1))

    closeness_coefficients = euclidean_distance_negative_ideal / \
        (euclidean_distance_ideal + euclidean_distance_negative_ideal)
    return closeness_coefficients


def check_numeric_values(data):
    try:
        numeric_columns = data.iloc[:, 1:].apply(
            pd.to_numeric, errors='coerce').notnull().all(axis=0)
        return numeric_columns.all()
    except Exception as e:
        print(f"Error checking numeric values: {e}")
        return False


def check_consistency(weights, impacts, data):
    try:
        return len(weights) == len(impacts) == len(data.columns) - 1
    except Exception as e:
        print(f"Error checking consistency: {e}")
        return False


def check_impacts(impacts):
    try:
        return all(impact in [-1, 1] for impact in impacts)
    except Exception as e:
        print(f"Error checking impacts: {e}")
        return False


def write_results(result_file, results):
    df = pd.DataFrame({'Values': results})
    df['Rank'] = (len(df) + 1) - df['Values'].rank()
    df.to_csv(result_file, index=False)
    print(f"Results have been saved to {result_file}")


def topsis(input_file, weights, impacts, result_file):
    data = read_data(input_file)
    if data is None:
        return

    weights_array, impacts_array = parse_weights_and_impacts(weights, impacts)

    if not check_columns(data) or not check_numeric_values(data) or not check_consistency(weights_array, impacts_array, data) or not check_impacts(impacts_array):
        print("Input conditions not met. Exiting.")
        return

    normalized_data = normalize_data(data)
    results = perform_topsis(normalized_data, weights_array, impacts_array)
    write_results(result_file, results)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "Usage: python topsis.py <InputDataFile> <Weights> <Impacts> <ResultFileName>")
    else:
        input_file = sys.argv[1]
        weights = sys.argv[2]
        impacts = sys.argv[3]
        result_file = sys.argv[4]

        topsis(input_file, weights, impacts, result_file)
