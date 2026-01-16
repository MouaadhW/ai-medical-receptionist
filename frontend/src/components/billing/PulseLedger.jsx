import React, { useState, useEffect } from 'react';
import GlassCard from '../shared/GlassCard';
import './billing.css';

const PulseLedger = () => {
    const [bills, setBills] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedBill, setSelectedBill] = useState(null);
    const [filter, setFilter] = useState('all');  // all, paid, pending, overdue

    useEffect(() => {
        fetchBills();
    }, []);

    const fetchBills = async () => {
        try {
            // Get current patient ID from context or props
            const patientId = 1; // TODO: Get from auth context
            const response = await fetch(`http://localhost:8000/api/billing/patient/${patientId}`);
            const data = await response.json();
            setBills(data.bills || []);
        } catch (error) {
            console.error('Error fetching bills:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredBills = bills.filter(bill => {
        if (filter === 'all') return true;
        return bill.status === filter;
    });

    const calculateTotals = () => {
        return {
            totalBalance: bills.reduce((sum, bill) => sum + bill.patient_due, 0),
            totalPaid: bills.filter(b => b.status === 'paid').reduce((sum, bill) => sum + bill.total_amount, 0),
            pending: bills.filter(b => b.status === 'pending').reduce((sum, bill) => sum + bill.patient_due, 0)
        };
    };

    const totals = calculateTotals();

    if (loading) {
        return (
            <div className="pulse-ledger">
                <div className="skeleton" style={{ height: '400px' }}></div>
            </div>
        );
    }

    return (
        <div className="pulse-ledger animate-fadeInUp">
            <div className="ledger-header">
                <h1 className="gradient-text">💰 Pulse Ledger</h1>
                <p className="subtitle">Your transparent financial healthcare hub</p>
            </div>

            {/* Summary Cards */}
            <div className="summary-grid">
                <GlassCard variant="medium" animated glowColor="teal" className="summary-card">
                    <div className="summary-icon">💵</div>
                    <div className="summary-value">TND {totals.totalBalance.toFixed(2)}</div>
                    <div className="summary-label">Current Balance</div>
                </GlassCard>

                <GlassCard variant="medium" animated glowColor="lime" className="summary-card">
                    <div className="summary-icon">✅</div>
                    <div className="summary-value">TND {totals.totalPaid.toFixed(2)}</div>
                    <div className="summary-label">Total Paid</div>
                </GlassCard>

                <GlassCard variant="medium" animated glowColor="teal" className="summary-card">
                    <div className="summary-icon">⏳</div>
                    <div className="summary-value">TND {totals.pending.toFixed(2)}</div>
                    <div className="summary-label">Pending</div>
                </GlassCard>

                <GlassCard variant="medium" animated glowColor="violet" className="summary-card">
                    <div className="summary-icon">📊</div>
                    <div className="summary-value">{bills.length}</div>
                    <div className="summary-label">Total Bills</div>
                </GlassCard>
            </div>

            {/* Filters */}
            <div className="filter-bar glass">
                <button
                    className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
                    onClick={() => setFilter('all')}
                >
                    All
                </button>
                <button
                    className={`filter-btn ${filter === 'pending' ? 'active' : ''}`}
                    onClick={() => setFilter('pending')}
                >
                    Pending
                </button>
                <button
                    className={`filter-btn ${filter === 'paid' ? 'active' : ''}`}
                    onClick={() => setFilter('paid')}
                >
                    Paid
                </button>
                <button
                    className={`filter-btn ${filter === 'overdue' ? 'active' : ''}`}
                    onClick={() => setFilter('overdue')}
                >
                    Overdue
                </button>
            </div>

            {/* Bills List */}
            <div className="bills-list">
                {filteredBills.length === 0 ? (
                    <GlassCard className="empty-state">
                        <p>No bills found</p>
                    </GlassCard>
                ) : (
                    filteredBills.map(bill => (
                        <GlassCard
                            key={bill.id}
                            variant="medium"
                            animated
                            glowColor="teal"
                            className="bill-card hover-lift"
                            onClick={() => window.location.href = `/billing/${bill.id}`}
                        >
                            <div className="bill-card-header">
                                <div>
                                    <div className="bill-number">{bill.bill_number}</div>
                                    <div className="bill-date">
                                        {new Date(bill.billed_date).toLocaleDateString()}
                                    </div>
                                </div>
                                <div className={`bill-status status-${bill.status}`}>
                                    {bill.status.toUpperCase()}
                                </div>
                            </div>

                            <div className="bill-card-body">
                                <div className="bill-amount-row">
                                    <span>Total Amount:</span>
                                    <span className="amount">TND {bill.total_amount.toFixed(2)}</span>
                                </div>
                                {bill.insurance_covered > 0 && (
                                    <div className="bill-amount-row insurance">
                                        <span>Insurance Covered:</span>
                                        <span className="amount">-TND {bill.insurance_covered.toFixed(2)}</span>
                                    </div>
                                )}
                                <div className="bill-amount-row total">
                                    <span>You Pay:</span>
                                    <span className="amount">TND {bill.patient_due.toFixed(2)}</span>
                                </div>
                            </div>

                            <div className="bill-card-footer">
                                <button className="btn-view">View Details →</button>
                            </div>
                        </GlassCard>
                    ))
                )}
            </div>
        </div>
    );
};

export default PulseLedger;
