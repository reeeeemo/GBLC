'use client';
import { useState, useEffect } from 'react';
import styles from './page.module.css';
import BondPredictionChart from './prediction_chart'

export default function Home() {
    const [message, setMessage] = useState('Loading...');
    const [error, setError] = useState(null);
    const [age, set_age] = useState('');
    const [init_invest, set_init_invest] = useState('')
    const [gender, set_gender] = useState('');
    const [loading, set_loading] = useState(false);
    const [predictions, set_predictions] = useState([]);
    const [life, set_life] = useState(0);

    const baseUrl = process.env.NODE_ENV === 'development'
        ? 'http://localhost:5328' // local flask serv
        : ''; // vercel prod

    useEffect(() => {
        fetch(`${baseUrl}/api/get_life_expec`)
            .then(response => response.json())
            .then(data => setMessage(data.message))
            .catch(err => setError('Error connecting to API: ' + err.message));
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        set_loading(true);
        setError(null);

        try {
            // Get Life Expectancy data
            const life_expec_response = await fetch(`${baseUrl}/api/get_life_expec`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    age: parseInt(age),
                    gender: gender
                })
            });

            const life_json = await life_expec_response.json();

            const life_value = parseInt(life_json.message)
            set_life(life_value)

            // Get Inflation + Bond Rate Of Return data
            const prediction_response = await fetch(`${baseUrl}/api/get_predictions`, {
                method: 'POST',
                headers: {
                        'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    age: life_value,
                    init_invest: parseInt(init_invest),
                }),
            });

            const predictions_json = await prediction_response.json();

            const pred_data = []

            predictions_json.prediction_data.forEach(function (prediction, index) {
                prediction.year = parseInt(prediction.year);
                prediction.short = parseFloat(prediction.short);
                prediction.med = parseFloat(prediction.med);
                prediction.long = parseFloat(prediction.long);
                prediction.inflation = parseFloat(prediction.inflation);

                pred_data.push(prediction);
            });

            console.log(pred_data);
            set_predictions(pred_data);

            setMessage(`Total Return: $${parseFloat(predictions_json.final_amount).toFixed(2)}`)
            
        } catch (err) {
            setError('Error submitting data: ' + err.message);
        }
    };

    return (
        <div className={styles.page}>
            <main className={styles.main}>
                <div className={styles.calculator}>
                    <h1 style={{
                        fontSize: '1.5rem',
                        fontWeight: 'bold',
                        marginBottom: '1.5rem',
                        textAlign: 'center'
                    }}>
                        Government Life Bond Calculator
                    </h1>
                    <form onSubmit={handleSubmit} style={{ marginBottom: '1rem' }}>
                        <div className={styles.inputGroup}>
                            <label className={styles.label}>Gender</label>
                            <div className={styles.genderButtons}>
                                <label className={`${styles.genderButton} ${gender === 'male' ? styles.selected : ''}`}>
                                    <input
                                        type="radio"
                                        name="gender"
                                        value="male"
                                        checked={gender === 'male'}
                                        onChange={(e) => set_gender(e.target.value)}
                                        className={styles.radioInput}
                                    />
                                    Male
                                </label>
                                <label className={`${styles.genderButton} ${gender === 'female' ? styles.selected : ''}`}>
                                    <input
                                        type="radio"
                                        name="gender"
                                        value="female"
                                        checked={gender === 'female'}
                                        onChange={(e) => set_gender(e.target.value)}
                                        className={styles.radioInput}
                                    />
                                    Female
                                </label>
                            </div>
                        </div>
                        <div className={styles.left}>
                            <label htmlFor="age" className={styles.label}>
                            Age
                            </label>
                            <input
                                id="age"
                                type="number"
                                value={age}
                                onChange={(e) => set_age(e.target.value)}
                                placeholder="Enter your age"
                                className={styles.input}
                                min="0"
                                step="1"
                                required
                            />
                        </div>
                        <div className={styles.right}>
                            <label htmlFor="init_invest" className={styles.label}>
                                Initial Investment
                            </label>
                            <input
                                id="init_invest"
                                type="number"
                                value={init_invest}
                                onChange={(e) => set_init_invest(e.target.value)}
                                placeholder="Enter your Initial Investment"
                                className={styles.input}
                                min="0"
                                step="1"
                                required
                            />
                        </div>
                        <button
                            type="submit"
                            className={styles.primary}
                            style={{
                                width: '100%',
                                padding: '0.5rem 1rem',
                                borderRadius: '6px'
                            }}
                            disabled={loading}
                        >
                            {loading ? 'Calculating...' : 'Calculate' }
                        </button>
                    </form>
                    {error ? (
                        <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>
                    ) : (
                            <p style={{ textAlign: 'center' }}>{message}</p>
                    )}
                </div>
                <BondPredictionChart predictions={predictions} />
            </main>
        </div>
    );
}