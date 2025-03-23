import math
import os
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import argparse
import sys
import csv  # Add import for CSV handling

def read_segments(file_path, diameter):
    with open(file_path, 'r') as file:
        segments = []
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    theta, r = map(float, line.split())
                    r *= diameter / 2  # Scale the distance to the specified diameter
                    # Convert polar to Cartesian coordinates
                    x = r * math.cos(theta)
                    y = r * math.sin(theta)
                    segments.append((x, y, theta, r))  # Store Cartesian (x, y) and original polar (theta, r)
                except ValueError:
                    print(f"Skipping invalid line in file {file_path}: {line}")
    return segments

def write_segments(file_path, segments):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as file:
        for segment in segments:
            file.write(f"{segment[0]} {segment[1]}\n")

def filter_segments(segments, threshold_percent, diameter):
    print(f"Filtering segments with threshold percent {threshold_percent}% and diameter {diameter}...")
    threshold_distance = (threshold_percent / 100) * diameter
    if threshold_distance == 0:  # Prevent division by zero
        print("Threshold distance is zero, skipping filtering.")
        return segments
    filtered_segments = [segments[0]]
    for i in range(1, len(segments)):
        x1, y1, _, _ = segments[i-1]
        x2, y2, _, _ = segments[i]
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if distance >= threshold_distance:
            filtered_segments.append(segments[i])
    print(f"Filtered down to {len(filtered_segments)} segments.")
    return filtered_segments

def generate_histogram(segments, n_buckets):
    print(f"Generating histogram with {n_buckets} buckets...")
    distances = []
    for i in range(1, len(segments)):
        r1, theta1 = segments[i-1]
        r2, theta2 = segments[i]
        distance = math.sqrt(r1**2 + r2**2 - 2*r1*r2*math.cos(theta2 - theta1))
        distances.append(distance)
    
    plt.hist(distances, bins=n_buckets)
    plt.xlabel('Distance (mm)')
    plt.ylabel('Frequency')
    plt.title('Histogram of Path Lengths (mm)')
    plt.show(block=True)  # Change block to True to delay until viewer dismisses it
    print("Histogram generated.")

def douglas_peucker(segments, epsilon, max_deviation):
    print(f"Applying Douglas-Peucker algorithm with epsilon {epsilon} ...")
    def perpendicular_distance(point, start, end):
        if start == end:
            # If start and end points are the same, return the distance from the point to the start
            return math.sqrt((point[0] - start[0]) ** 2 + (point[1] - start[1]) ** 2)
        else:
            d = math.sqrt((end[1] - start[1]) ** 2 + (end[0] - start[0]) ** 2)
            if d == 0:  # Prevent division by zero
                return 0
            n = abs((end[1] - start[1]) * point[0] - (end[0] - start[0]) * point[1] + end[0] * start[1] - end[1] * start[0])
            return n / d

    def rdp(points, epsilon, max_deviation):
        if len(points) < 2:  # Ensure there are at least two points
            return points
        dmax = 0.0
        index = 0
        end = len(points)
        for i in range(1, end - 1):
            d = perpendicular_distance(points[i][:2], points[0][:2], points[end - 1][:2])  # Use only (x, y) for distance calculation
            if dmax >= max_deviation:
                break
            if d > dmax:
                index = i
                dmax = d
        if dmax >= epsilon and dmax <= max_deviation:
            results1 = rdp(points[:index + 1], epsilon, max_deviation)
            results2 = rdp(points[index:], epsilon, max_deviation)
            return results1[:-1] + results2
        else:
            return [points[0], points[end - 1]]

    result = rdp(segments, epsilon, max_deviation)
    return result

def display_file_contents(file_path, diameter):
    print(f"Contents of {file_path}:")
    segments = read_segments(file_path, diameter)
    plot_segments(segments, f"Segments from {file_path}")

def calculate_total_path_length(segments):
    total_length = 0.0
    for i in range(1, len(segments)):
        x1, y1, _, _ = segments[i-1]  # Extract Cartesian coordinates of the previous point
        x2, y2, _, _ = segments[i]    # Extract Cartesian coordinates of the current point
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)  # Calculate Euclidean distance
        total_length += distance
    return total_length

def plot_segments(segments, title, ax=None, color='white', linewidth=0.01):
    # Extract theta and r from the updated tuple structure
    theta = [segment[2] for segment in segments]  # Extract theta
    r = [segment[3] for segment in segments]      # Extract r
    num_segments = len(segments)
    if ax is None:
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
        ax.plot(theta, r, marker='o', color=color, linewidth=linewidth)
        ax.set_ylim(0, max(r))
        ax.set_title(f"{title} ({num_segments} segments)")
        ax.set_facecolor('#c9b17f')  # Light brown
        plt.show(block=True)
    else:
        ax.plot(theta, r, markersize=1, color=color, linewidth=1)
        ax.set_ylim(0, max(r))
        ax.set_title(f"{title} ({num_segments} segments)")
        ax.set_facecolor('#c9b17f')  # Light brown

def calculate_max_deviation(original_segments, processed_segments):
    deviations = []
    for i, (orig, proc) in enumerate(zip(original_segments, processed_segments)):
        deviation = math.sqrt((orig[0] - proc[0]) ** 2 + (orig[1] - proc[1]) ** 2)
        deviations.append((i, deviation))
    deviations.sort(key=lambda x: x[1], reverse=True)
    return deviations[:10]

def process_file(file_path, input_dir, output_dir, threshold_percent, diameter, n_buckets, epsilon, max_deviation, use_douglas_peucker, show_histogram, top_n_deviations, display_time, results):
    segments = read_segments(file_path, diameter)
    if not segments:  # Check if the segments list is empty
        print(f"No valid segments found in file: {file_path}. Skipping processing.")
        return

    original_length = calculate_total_path_length(segments)
    
    if use_douglas_peucker:
        processed_segments = douglas_peucker(segments, epsilon, max_deviation)
    else:
        processed_segments = filter_segments(segments, threshold_percent, diameter)
    
    # Ensure the start and end points remain untouched
    if len(processed_segments) > 1:  # Ensure there are at least two segments
        processed_segments[0] = segments[0]
        processed_segments[-1] = segments[-1]
    
    processed_length = calculate_total_path_length(processed_segments)
    max_deviation_list = calculate_max_deviation(segments, processed_segments)
    max_deviation = max(max_deviation_list, key=lambda x: x[1])[1] if max_deviation_list else 0.0
    
    relative_path = os.path.relpath(file_path, input_dir)
    output_file_path = os.path.join(output_dir, relative_path)
    write_segments(output_file_path, processed_segments)
    
    file_name = os.path.basename(file_path)
    print(f"{file_name}: Original segments: {len(segments)}, Processed segments: {len(processed_segments)}, Original length: {original_length:.2f} mm, Processed length: {processed_length:.2f} mm")
    
    # Append results for CSV
    results.append([file_name, len(segments), len(processed_segments), f"{original_length:.2f}", f"{processed_length:.2f}", f"{max_deviation:.2f}"])
    
    fig, axs = plt.subplots(1, 3, figsize=(21, 7), subplot_kw={'projection': 'polar'})
    plot_segments(segments, 'Original Segments', ax=axs[0], color='white', linewidth=0.01)
    plot_segments(processed_segments, 'Processed Segments', ax=axs[1], color='white', linewidth=0.01)
    
    # Plot the top n deviations in red on the third graph
    plot_segments(processed_segments, 'Processed Segments with Deviations', ax=axs[2], color='white', linewidth=0.01)
    if top_n_deviations > 0:
        top_deviations = max_deviation_list[:top_n_deviations]
        top_deviation_points = [segments[index] for index, _ in top_deviations]
        theta = [point[2] for point in top_deviation_points]  # Extract theta
        r = [point[3] for point in top_deviation_points]      # Extract r
        axs[2].plot(theta, r, 'ro', markersize=5)
    
    axs[0].set_title(f'Original Segments ({len(segments)} segments)')
    axs[1].set_title(f'Processed Segments ({len(processed_segments)} segments)')
    axs[2].set_title(f'Processed Segments with Deviations ({len(processed_segments)} segments)')
    plt.suptitle(f"File: {file_name}")
    
    if display_time > 0:
        plt.pause(display_time)
    else:
        plt.show(block=True)
    
    plt.close()
    
    if show_histogram:
        generate_histogram(processed_segments, n_buckets)

def process_files(input_path, output_dir, threshold_percent, diameter, n_buckets, epsilon, max_deviation, use_douglas_peucker, show_histogram, top_n_deviations, display_time, csv_file=None):
    results = []  # List to store results for CSV
    if os.path.isfile(input_path):
        process_file(input_path, os.path.dirname(input_path), output_dir, threshold_percent, diameter, n_buckets, epsilon, max_deviation, use_douglas_peucker, show_histogram, top_n_deviations, display_time, results)
    else:
        for root, _, files in os.walk(input_path):
            for file in files:
                file_path = os.path.join(root, file)
                process_file(file_path, input_path, output_dir, threshold_percent, diameter, n_buckets, epsilon, max_deviation, use_douglas_peucker, show_histogram, top_n_deviations, display_time, results)
    
    # Write results to CSV if csv_file is provided
    if csv_file:
        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['File Name', 'Original Segments', 'Processed Segments', 'Original Length (mm)', 'Processed Length (mm)', 'Max Deviation (mm)'])
            writer.writerows(results)
        print(f"Results saved to CSV file: {csv_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process and trim path segments.')
    parser.add_argument('--input_path', help='Input file or directory containing files to process')
    parser.add_argument('--output_dir', help='Output directory to save processed files')
    parser.add_argument('--threshold_percent', type=float, default=0.5, help='Threshold percent for filtering segments (default: 0.5)')
    parser.add_argument('--diameter', type=float, default=33, help='Diameter of the circle (default: 40)')
    parser.add_argument('--n_buckets', type=int, default=200, help='Number of buckets for the histogram (default: 10)')
    parser.add_argument('--epsilon', type=float, default=.001, help='Epsilon value for Douglas-Peucker algorithm. A reasonable range is 0.1 to 10.0. It determines the maximum distance a point can deviate from the line before it is considered significant.')
    parser.add_argument('--max_deviation', type=float, default=float('inf'), help='Maximum deviation allowed for a point to be removed (default: infinity)')
    parser.add_argument('--use_douglas_peucker', action='store_true', default=True, help='Use Douglas-Peucker algorithm for trimming segments (default: True)')
    parser.add_argument('--show_histogram', action='store_true', help='Show histogram of path lengths')
    parser.add_argument('--top_n_deviations', type=int, default=1000, help='Number of top deviations to display on the processed graph (default: 0)')
    parser.add_argument('--display_time', type=float, default=5.0, help='Time to display each plot in seconds (default: 5.0)')
    parser.add_argument('--csv_file', help='CSV file to save processing information for all processed files')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if args.use_douglas_peucker and args.epsilon is None:
        parser.error("--epsilon is required when --use_douglas_peucker is specified")

    process_files(args.input_path, args.output_dir, args.threshold_percent, args.diameter, args.n_buckets, args.epsilon, args.max_deviation, args.use_douglas_peucker, args.show_histogram, args.top_n_deviations, args.display_time, args.csv_file)