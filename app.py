import os
from flask import Flask, render_template, request, jsonify # type: ignore
import joblib # type: ignore
import numpy as np # type: ignore
import pandas as pd # type: ignore
import pycaret

# Initialize the Flask application
app = Flask(__name__)

# Load the pre-trained model from the specified file
model = joblib.load('model/my_residential_pipeline.pkl')

# Define the home route which renders the HTML form
@app.route('/')
def home():
    # Render the index.html template when the root URL is accessed
    return render_template('index.html')

# Define the prediction route which processes the form data
@app.route('/predict', methods=['POST'])
def predict():
    # Convert form data from the request to a dictionary
    data = request.form.to_dict()

    # Add default values for missing features (required by the model pipeline)
    # These defaults are necessary to ensure that all features the model expects are present
    data['block'] = 'default_block'
    data['street_name'] = 'default_street_name'
    data['town'] = 'default_town'
    data['month'] = 'default_month'
    data['flat_model'] = 'default_flat_model'
    data['latitude'] = 0.0
    data['longitude'] = 0.0
    data['postal_code'] = '000000'

    # Convert the dictionary to a pandas DataFrame, as required by the model
    input_data = pd.DataFrame([data])

    # Ensure that numeric fields are of the correct data type
    # This step is crucial because the model expects these inputs in specific formats
    input_data['floor_area_sqm'] = input_data['floor_area_sqm'].astype(float)
    input_data['lease_commence_date'] = input_data['lease_commence_date'].astype(int)
    input_data['cbd_dist'] = input_data['cbd_dist'].astype(float)
    input_data['min_dist_mrt'] = input_data['min_dist_mrt'].astype(float)

    # Print the input data for debugging purposes
    # This helps verify that the input data is being processed correctly
    print("Input data:\n", input_data)

    # Add necessary features with default values, using .get() for safety
    # This ensures that if a key is missing, the default value will be used
    input_data['block'] = input_data.get('block', 'default')
    input_data['street_name'] = input_data.get('street_name', 'default')
    input_data['town'] = input_data.get('town', 'default')
    input_data['month'] = input_data.get('month', '01-2022')
    input_data['flat_model'] = input_data.get('flat_model', 'default')
    input_data['latitude'] = input_data.get('latitude', 0.0)
    input_data['longitude'] = input_data.get('longitude', 0.0)

    # Make a prediction using the model; the model expects the input data as a DataFrame
    log_prediction = model.predict(input_data)

    # Print the raw prediction (logarithmic resale price) for debugging
    # This helps in understanding what the model is outputting before any transformations
    print("Raw prediction from model:", log_prediction)

    # Convert the logarithmic resale price back to the actual price
    # The model outputs a log-transformed price, so we exponentiate to get the real price
    prediction = np.exp(log_prediction)

    # Round the prediction to 2 decimal places for better readability
    rounded_prediction = round(prediction[0], 2)
    
    # Format the prediction as a currency string (e.g., $123,456.78)
    formatted_prediction = "${:,.2f}".format(rounded_prediction)
    
    # Return the prediction as a JSON response, which will be displayed in the web app
    return jsonify({'prediction': formatted_prediction})

# Run the Flask app in debug mode; this allows for real-time error feedback during development
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


#Explanation of Complex Steps:

# 1. Default Values for Missing Features:
#Default values are assigned to features that might be missing from the form input. This is essential because the model pipeline 
# expects these features to be present, even if they are not relevant or provided by the user. Without these defaults, the model 
# could raise errors about missing columns.

# 2. Data Conversion and Validation:
#The form inputs for floor_area_sqm, lease_commence_date, cbd_dist, and min_dist_mrt are explicitly converted to the correct data 
# types (float or int). This is critical because the model's training data likely had these fields in specific formats, and any 
# deviation could cause the model to produce errors or incorrect predictions.

# 3. Log-Transformation Handling:
#Since the model was trained to predict the log of the resale price, the raw prediction must be exponentiated (np.exp(log_prediction)) 
# to convert it back to the original scale. This step is crucial to getting a meaningful resale price rather than a logarithmic 
# value.