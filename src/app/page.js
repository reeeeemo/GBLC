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
    const [predictions, set_predictions] = useState(["", []]);
    const [future_dates, set_future_dates] = useState(["", []]);
    const [life, set_life] = useState(0);
    const [inflation, set_inflation] = useState([])

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

            const inflation_response = await fetch(`${baseUrl}/api/get_inflation`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    life: life_value
                })
            })

            const inflation = await inflation_response.json();

            set_inflation(inflation.predictions)

            const bond_response = await fetch(`${baseUrl}/api/get_bond`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    life: life_value
                })
            })

            const bond = await bond_response.json();

            set_predictions([
                ["short", bond.short_predictions],
                ["med", bond.med_predictions],
                ["long", bond.long_predictions]
            ]);

            set_future_dates([
                ["short", bond.short_dates],
                ["med", bond.med_dates],
                ["long", bond.long_dates]
            ])

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
                <BondPredictionChart predictions={predictions} future_dates={future_dates} inflation={inflation} />
            </main>
        </div>
    );
}