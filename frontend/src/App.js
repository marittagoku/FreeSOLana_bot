import React, { useEffect, useState } from "react";
import "./App.css";

const API_URL = "https://freesolana-bot.onrender.com";

function App() {
  const [balance, setBalance] = useState(null);
  const [userId, setUserId] = useState("867950891");

  useEffect(() => {
    fetch(`${API_URL}/balance/${userId}`)
      .then((res) => res.json())
      .then((data) => {
        if (data && typeof data.balance === "number") {
          setBalance(data.balance.toFixed(2));
        } else {
          setBalance("Errore");
        }
      })
      .catch(() => setBalance("Errore"));
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-purple-800 to-purple-900 p-6">
      <div className="text-center bg-purple-700 p-6 rounded-2xl shadow-2xl">
        <h1 className="text-3xl font-bold text-white mb-4">
          🪙 Saldo Attuale
        </h1>
        <div className="text-4xl font-extrabold text-green-400 mb-4">
          {balance === null ? "Caricamento..." : `${balance} €`}
        </div>
        <p className="text-white text-sm">ID Utente: {userId}</p>
      </div>
      <div className="absolute bottom-4 w-full text-center text-white/50 text-sm">
        @SolanaFreeDrop_bot
      </div>
    </div>
  );
}

export default App;
