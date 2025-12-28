import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);

    const API_URL = 'http://localhost:8000/api/auth';

    useEffect(() => {
        const loadUser = async () => {
            if (token) {
                try {
                    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
                    const res = await axios.get(`${API_URL}/me`);
                    setUser(res.data);
                } catch (error) {
                    console.error("Error loading user", error);
                    logout();
                }
            }
            setLoading(false);
        };
        loadUser();
    }, [token]);

    const login = async (username, password) => {
        const params = new URLSearchParams();
        params.append('username', username);
        params.append('password', password);

        const res = await axios.post(`${API_URL}/login`, params, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });
        const { access_token, role, otid } = res.data;

        localStorage.setItem('token', access_token);
        setToken(access_token);
        // We will fetch full user data in useEffect, or set it here
        // Setting it here for immediate feedback is good, but waiting for useEffect is safer?
        // Let's rely on loadUser from useEffect or just call it.
        // Actually, simpler to just set defaults headers and reload user.
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        const userRes = await axios.get(`${API_URL}/me`);
        setUser(userRes.data);
        return userRes.data;
    };

    const register = async (username, email, password) => {
        const res = await axios.post(`${API_URL}/register`, { username, email, password });
        return res.data;
    };

    const logout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
        delete axios.defaults.headers.common['Authorization'];
    };

    return (
        <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
