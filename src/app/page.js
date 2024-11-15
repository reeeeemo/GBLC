'use client';
import { useState, useEffect } from 'react';

export default function Home() {
    const [message, setMessage] = useState('Loading...');
    const [error, setError] = useState(null);

    useEffect(() => {
        // In development (localhost)
        const apiUrl = process.env.NODE_ENV === 'development'
            ? 'http://localhost:5328/api/hello'  // Local Flask server
            : '/api/hello';  // Production on Vercel

        fetch(apiUrl)
            .then(response => response.json())
            .then(data => setMessage(data.message))
            .catch(err => setError('Error connecting to API: ' + err.message));
    }, []);

    return (
        <main className="p-4">
            <h1 className="text-2xl mb-4">API Test</h1>
            {error ? (
                <p className="text-red-500">{error}</p>
            ) : (
                <p>Message from API: {message}</p>
            )}
        </main>
    );
}