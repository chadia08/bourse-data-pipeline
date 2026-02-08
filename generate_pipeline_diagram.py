"""
Data Pipeline Architecture Diagram Generator
Generates a visual representation of the data pipeline architecture
showing connections between Kafka, ClickHouse, PowerBI, and MongoDB
"""

from graphviz import Digraph

def create_pipeline_diagram():
    """
    Create a data pipeline architecture diagram showing:
    - kafka -> clickhouse
    - clickhouse -> powerbi
    - clickhouse -> mongodb
    """
    # Create a new directed graph
    dot = Digraph(comment='Data Pipeline Architecture', format='png')
    dot.attr(rankdir='LR')  # Left to right layout
    dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue', 
             fontname='Arial', fontsize='12')
    dot.attr('edge', color='#2c3e50', penwidth='2', arrowsize='0.8')
    
    # Define nodes with custom styling
    dot.node('kafka', 'Kafka\n(Message Broker)', fillcolor='#ff6b6b', fontcolor='white')
    dot.node('clickhouse', 'ClickHouse\n(Data Warehouse)', fillcolor='#4ecdc4', fontcolor='white')
    dot.node('powerbi', 'Power BI\n(Analytics)', fillcolor='#feca57', fontcolor='black')
    dot.node('mongodb', 'MongoDB\n(Database)', fillcolor='#48dbfb', fontcolor='white')
    
    # Define edges (connections)
    dot.edge('kafka', 'clickhouse', label='Stream Data')
    dot.edge('clickhouse', 'powerbi', label='Reporting')
    dot.edge('clickhouse', 'mongodb', label='Export Data')
    
    # Graph styling
    dot.attr(bgcolor='white', pad='0.5')
    
    # Save the diagram
    output_path = 'pipeline_architecture'
    dot.render(output_path, cleanup=True)
    print(f"✓ Diagram generated successfully: {output_path}.png")
    
    return f"{output_path}.png"

if __name__ == '__main__':
    create_pipeline_diagram()
