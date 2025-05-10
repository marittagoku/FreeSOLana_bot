import React, { useEffect, useState } from "react";

function App() {
  const [balance, setBalance] = useState(null);
  const [userId, setUserId] = useState(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const id = params.get("id");
    setUserId(id);

    if (id) {
      fetch(`https://freesolana-api.onrender.com/balance/${id}`)
        .then((res) => res.json())
        .then((data) => {
          if (data.balance !== undefined) {
            setBalance(data.balance.toFixed(2));
          } else {
            setBalance("Errore");
          }
        })
        .catch((err) => {
          console.error("Errore nel recupero del saldo:", err);
          setBalance("Errore");
        });
    }
  }, []);

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-purple-900 to-indigo-900 text-white font-sans p-4">
      <div className="bg-black bg-opacity-20 rounded-2xl shadow-xl p-6 w-full max-w-md">
        <h1 className="text-3xl font-bold mb-6 text-center">💰 Saldo Attuale</h1>
        <div className="text-center text-5xl font-extrabold text-green-400 mb-6">
          {balance === null ? "Caricamento..." : `${balance} €`}
        </div>
        <div className="text-center text-sm text-gray-300 mt-4">
          ID Utente: {userId || "N/D"}
        </div>
      </div>
    </div>
  );
}

export default App;
