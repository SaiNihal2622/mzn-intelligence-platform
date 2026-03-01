import { useState } from 'react';
import { Send, FileText, Globe, MapPin, Loader2, Wand2 } from 'lucide-react';

export default function InputPanel({ onSubmit, isAnalyzing }) {
    const [formData, setFormData] = useState({
        sector: '',
        region: '',
        project_description: '',
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!formData.sector || !formData.region || !formData.project_description) return;
        onSubmit(formData);
    };

    const handleAutofill = () => {
        setFormData({
            sector: 'climate',
            region: 'East Africa',
            project_description: 'Community-based climate adaptation program focusing on drought-resistant agriculture and strategic alternative livelihoods for smallholder farmers. The program requires immediate establishment of water harvesting infrastructure and local capacity building to ensure long term sustainability of yields.',
        });
    };

    return (
        <div className="glass-panel">
            <div className="glass-header">
                <h2 className="text-lg font-semibold" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <FileText style={{ color: 'var(--accent-blue)', width: '20px', height: '20px' }} />
                    Project Context Analysis
                </h2>
                <button
                    type="button"
                    onClick={handleAutofill}
                    className="btn btn-ghost"
                >
                    <Wand2 style={{ width: '14px', height: '14px' }} />
                    Example Input
                </button>
            </div>

            <form onSubmit={handleSubmit} style={{ padding: '1.5rem' }}>
                <div className="grid-2">
                    <div className="form-group">
                        <label htmlFor="sector" className="input-label">Primary Sector</label>
                        <div className="input-wrapper">
                            <Globe className="input-icon" />
                            <select
                                id="sector"
                                name="sector"
                                value={formData.sector}
                                onChange={handleChange}
                                className="form-input with-icon"
                                required
                            >
                                <option value="" disabled>Select sector...</option>
                                <option value="climate">Climate & Environment</option>
                                <option value="health">Health & Nutrition</option>
                                <option value="education">Education</option>
                                <option value="governance">Governance & Civil Society</option>
                                <option value="wash">WASH</option>
                                <option value="economic">Economic Development</option>
                            </select>
                        </div>
                    </div>

                    <div className="form-group">
                        <label htmlFor="region" className="input-label">Target Region</label>
                        <div className="input-wrapper">
                            <MapPin className="input-icon" />
                            <select
                                id="region"
                                name="region"
                                value={formData.region}
                                onChange={handleChange}
                                className="form-input with-icon"
                                required
                            >
                                <option value="" disabled>Select region...</option>
                                <option value="East Africa">East Africa</option>
                                <option value="West Africa">West Africa</option>
                                <option value="South Asia">South Asia</option>
                                <option value="Latin America">Latin America & Caribbean</option>
                                <option value="Pacific Islands">Pacific Islands</option>
                                <option value="Global">Global / Multi-region</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div className="form-group">
                    <label htmlFor="project_description" className="input-label">
                        Project Description & Objectives
                    </label>
                    <textarea
                        id="project_description"
                        name="project_description"
                        rows={5}
                        value={formData.project_description}
                        onChange={handleChange}
                        className="form-input"
                        placeholder="Describe the core problem, target beneficiaries, and proposed interventions..."
                        required
                    />
                    <p className="text-xs text-muted mt-2">
                        Tip: Be specific about the interventions to ensure accurate finding matches.
                    </p>
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1.5rem' }}>
                    <button
                        type="submit"
                        disabled={isAnalyzing || !formData.sector || !formData.region || !formData.project_description}
                        className="btn btn-primary"
                    >
                        {isAnalyzing ? (
                            <>
                                <Loader2 className="animate-spin" style={{ width: '16px', height: '16px' }} />
                                Processing Analysis...
                            </>
                        ) : (
                            <>
                                <Send style={{ width: '16px', height: '16px' }} />
                                Run Intelligence Pipeline
                            </>
                        )}
                    </button>
                </div>
            </form>
        </div>
    );
}
