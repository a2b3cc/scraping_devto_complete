# source/analysis/initial_analysis.py
import ast
from pathlib import Path

import matplotlib.colors
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import squarify
import numpy as np
from config import EXPORT_IMAGE_DIR

def load_latest_data():
    """
    Loads the latest CSV in the dataset/ path.
    Returns:
        pd.DataFrame
    """
    # Get the latest CSV dataset
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_dir = base_dir / "dataset"
    csv_files = sorted(data_dir.glob("devto_data_*.csv"))

    if not csv_files:
        print("No CSV files found")
        return pd.DataFrame()
    else:
        latest_file = csv_files[-1]
        df = pd.read_csv(latest_file)
        df["tags"] = df["tags"].apply(ast.literal_eval)
        df["comments"] = df["comments"].apply(ast.literal_eval)
        return df

def print_summary(df: pd.DataFrame):
    """"
    Prints summary information of a DataFrame including
    number of rows and columns, data types, non-null counts and
    descriptive statistics.
    """
    print(f"DataFrame shape: {df.shape[0]} rows, {df.shape[1]} columns")

    print("DataFrame info:")
    print(df.info())

    print("DataFrame descriptive statistics:")
    print(df.describe())


def export_fig(fig, filename: str, dpi: int = 300):
    """
    Saves the given figure to the export directory with given filename.
    Args:
        fig: matplotlib figure to save.
        filename: name of the figure.
        dpi: resolution of the saved image.

    Returns:
        None
    """
    # Export to path
    export_dir = Path(__file__).resolve().parent / EXPORT_IMAGE_DIR
    export_dir.mkdir(parents=True, exist_ok=True)
    file_dir = export_dir / filename
    fig.savefig(file_dir, dpi=300)


def plot_metrics_by_group(df: pd.DataFrame, group_by: str):
    """
    Exports a horizontal barplot showing the patterns for the average
    number of reactions, comments and read time for each topic.
    Args:
        df: article DataFrame with columns "topic" and "trending_period".
        group_by: column name to group by, only accepts "topic" or "trending_period".
    Returns:
        None
    """
    # Parameter validation
    accepted_groupings = {"topic", "trending_period"}
    if group_by not in accepted_groupings:
        raise ValueError(f"The column '{group_by}' does not exist in the DataFrame. "
                         f"Accepted values are: {', '.join(accepted_groupings)}.")

    # Dictionary to map colors for article metrics
    metrics_colors = {
        "read_time_minutes": "#3498db",
        "reaction_count": "#f39c12",
        "comments_count": "#2ecc71"
    }
    labels = ["Reading Minutes", "Number of Reactions", "Number of Comments"]
    # Compute average metrics
    avg_metrics = df.groupby(group_by)[list(metrics_colors.keys())].mean().reset_index()

    # Distribute the groups on the y axis
    groups = avg_metrics[group_by]
    y_coords = np.arange(len(groups))

    # Create a barplot subplot for each metric
    fig, axs = plt.subplots(1, 3, figsize=(14,6))
    axs = axs.flatten()

    for ax, (metric, color), label in zip(axs, metrics_colors.items(), labels):
        ax.barh(y_coords, avg_metrics[metric], color=color, label=label)
        ax.set_title(label, color=color)

    # Remove ticks and spines for a cleaner graph
    for i, ax in enumerate(axs):
        if i > 0:
            ax.set_yticklabels([])
        ax.tick_params(axis="both", which="both", length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)

    # Only show labels in the left first subplot
    axs[0].set_yticks(y_coords)
    axs[0].set_yticklabels(groups)

    # Figure title
    title = group_by.replace("_", " ").capitalize()
    fig.suptitle(f"DEV.to Article Metrics by {title}", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Export figure
    export_fig(fig, f"DEVto_metrics_by_{title}.png")


def plot_tags_treemap_for_topic(tag_counts_topic: pd.Series, topic: str,
                           count_threshold: int = 5):
    """
    Plots a treemap of tag counts for one topic, sorted in descending count order.
    Excludes tags below the given count threshold and the topic itself.
    Args:
        tag_counts_topic: a series with tag counts for a specific topic.
        topic: topic name.
        count_threshold: minimum count required for a tag to be plotted.

    Returns:
        None
    """
    # Exclude the topic from the tag counts
    if topic in tag_counts_topic.index:
        tag_counts_topic.drop(topic, inplace=True)

    # Filter by count threshold
    tag_counts_topic = tag_counts_topic[tag_counts_topic >= count_threshold]

    if count_threshold < 0:
        tag_counts_topic = tag_counts_topic[tag_counts_topic > 0]

    if tag_counts_topic.empty:
        print(f"No tags for topic '{topic}' meet the threshold of {count_threshold}.")
        return
    # Sort in descending count order
    tag_counts_topic = tag_counts_topic.sort_values(ascending=False)

    # Labels and values
    labels = [f"{tag}\n{count}" for tag,count in tag_counts_topic.items()]
    sizes = tag_counts_topic.values
    # Colors
    cmap = matplotlib.cm.BuPu
    norm = matplotlib.colors.Normalize(vmin=min(sizes) - 70, vmax=max(sizes))
    colors = [cmap(norm(value)) for value in sizes]

    # Plot treemap
    fig, ax = plt.subplots(figsize=(14, 6))
    squarify.plot(sizes=sizes, label= labels, color=colors, alpha=0.8,
                  ax=ax, text_kwargs={'color': 'white'})
    fig.suptitle(f"Treemap of Tag Counts for Topic '{topic}'", fontsize=16)
    ax.invert_yaxis()
    ax.set_axis_off()

    # Export figure
    export_fig(fig, f"DEVto_tags_treemap_for_{topic}.png")


def plot_tags_treemap_for_all_topics(df: pd.DataFrame, count_threshold: int=5):
    """
    Exports a heatmap showing the count of tag occurrence for each topic.
    Excludes the topic "all", as it is not a real topic.
    Args:
        df: article DataFrame with columns "topic" and "tags".
        count_threshold: minimum total occurrence count for a tag to be plotted.
    Returns:
        None
    """
    # Filter out rows with topic "all"
    df_filtered = df[df["topic"] != "all"].copy()

    # Create dummy variables for each tag
    df_exploded = df_filtered.explode("tags")
    tag_dummies = pd.get_dummies(df_exploded["tags"])
    df_tags = pd.concat([df_exploded["topic"], tag_dummies], axis=1)

    # Group by topic and sum tag occurrences
    tag_counts = df_tags.groupby("topic").sum()
    topics = tag_counts.index.tolist()

    for topic in topics:
        plot_tags_treemap_for_topic(tag_counts.loc[topic], topic, count_threshold)


if __name__ == "__main__":
    # Load data
    df = load_latest_data()
    # Analysis
    print_summary(df)
    # Visualization
    plot_metrics_by_group(df, "topic")
    plot_metrics_by_group(df, "trending_period")
    plot_tags_treemap_for_all_topics(df)





