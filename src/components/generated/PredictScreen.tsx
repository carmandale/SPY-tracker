import React, { useState } from 'react';
import { PredictionForm } from '@/components/PredictionForm';
import { PredictionFormData } from '@/lib/schemas';

export function PredictScreen() {
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (data: PredictionFormData) => {
    setIsLoading(true);
    
    try {
      // Get current date in CST timezone
      const today = new Date().toLocaleDateString('en-CA', {
        timeZone: 'America/Chicago'
      });

      // Call the backend API
      const response = await fetch(`http://localhost:8000/prediction/${today}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Prediction saved successfully:', result);
    } catch (error) {
      console.error('Error saving prediction:', error);
      throw error; // Re-throw to let PredictionForm handle it
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <PredictionForm 
      onSubmit={handleSubmit} 
      isLoading={isLoading}
    />
  );
}