import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Save } from 'lucide-react';
import { Header } from '../components/layout/Header';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { api } from '../lib/api.js';

const INDUSTRIES = [
  'Technology',
  'AI/ML',
  'Fintech',
  'Healthcare',
  'E-commerce',
  'SaaS',
  'Blockchain',
  'Gaming',
  'EdTech',
  'Climate Tech',
];

const ROLES = [
  'Founder/CEO',
  'Product Manager',
  'Engineer',
  'Designer',
  'Marketer',
  'Investor',
  'Student',
  'Other',
];

export const PreferencesPage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Preferences state
  const [selectedIndustries, setSelectedIndustries] = useState<string[]>([]);
  const [companyInput, setCompanyInput] = useState('');
  const [companies, setCompanies] = useState<string[]>([]);
  const [role, setRole] = useState('');
  const [topics, setTopics] = useState('');
  const [emailTime, setEmailTime] = useState('08:00');
  const [emailFrequency, setEmailFrequency] = useState('daily');

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      const prefs = await api.getPreferences();
      setSelectedIndustries(prefs.industries || []);
      setCompanies(prefs.companies_to_track || []);
      setRole(prefs.role || '');
      setTopics((prefs.topics_of_interest || []).join(', '));
      setEmailTime(prefs.email_time || '08:00');
      setEmailFrequency(prefs.email_frequency || 'daily');
    } catch (error) {
      console.error('Failed to load preferences:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleIndustry = (industry: string) => {
    setSelectedIndustries((prev) =>
      prev.includes(industry)
        ? prev.filter((i) => i !== industry)
        : [...prev, industry]
    );
  };

  const addCompany = () => {
    if (companyInput.trim() && !companies.includes(companyInput.trim())) {
      setCompanies([...companies, companyInput.trim()]);
      setCompanyInput('');
    }
  };

  const removeCompany = (company: string) => {
    setCompanies(companies.filter((c) => c !== company));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.updatePreferences({
        industries: selectedIndustries,
        companies_to_track: companies,
        role,
        topics_of_interest: topics.split(',').map((t) => t.trim()).filter(Boolean),
        email_time: emailTime,
        email_frequency: emailFrequency,
      });
      navigate('/dashboard');
    } catch (error) {
      console.error('Failed to save preferences:', error);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen">
        <Header />
        <LoadingSpinner className="mt-20" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg-alt">
      <Header />

      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Back button */}
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 text-text-secondary hover:text-primary mb-6 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboard
        </button>

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-text-primary mb-2">
            Preferences
          </h1>
          <p className="text-text-secondary">
            Customize your daily digest content and delivery
          </p>
        </div>

        {/* Content */}
        <div className="space-y-8">
          {/* Industries */}
          <div className="bg-white rounded-xl p-8 shadow-md border border-border-light">
            <h2 className="text-xl font-semibold text-text-primary mb-4">
              Industries
            </h2>
            <p className="text-text-secondary mb-4">
              Select the industries you want to follow
            </p>
            <div className="flex flex-wrap gap-3">
              {INDUSTRIES.map((industry) => (
                <button
                  key={industry}
                  onClick={() => toggleIndustry(industry)}
                  className={`px-4 py-2.5 rounded-xl border-2 font-medium transition-all duration-200 ${
                    selectedIndustries.includes(industry)
                      ? 'border-primary bg-primary-pale text-primary shadow-sm'
                      : 'border-border-light hover:border-primary hover:bg-bg-soft text-text-primary'
                  }`}
                >
                  {industry}
                </button>
              ))}
            </div>
          </div>

          {/* Companies */}
          <div className="bg-white rounded-xl p-8 shadow-md border border-border-light">
            <h2 className="text-xl font-semibold text-text-primary mb-4">
              Companies to Track
            </h2>
            <p className="text-text-secondary mb-4">
              Get prioritized news about specific companies
            </p>
            <div className="space-y-4">
              <div className="flex gap-2">
                <Input
                  type="text"
                  value={companyInput}
                  onChange={(e) => setCompanyInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && addCompany()}
                  placeholder="e.g., OpenAI, Google, Apple"
                />
                <Button type="button" onClick={addCompany}>
                  Add
                </Button>
              </div>
              <div className="flex flex-wrap gap-2">
                {companies.map((company) => (
                  <Badge
                    key={company}
                    variant="company"
                    className="cursor-pointer hover:opacity-75"
                    onClick={() => removeCompany(company)}
                  >
                    {company} ✕
                  </Badge>
                ))}
              </div>
            </div>
          </div>

          {/* Role and Topics */}
          <div className="bg-white rounded-xl p-8 shadow-md border border-border-light">
            <h2 className="text-xl font-semibold text-text-primary mb-4">
              Your Profile
            </h2>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-text-primary mb-3">
                  Your role
                </label>
                <div className="flex flex-wrap gap-3">
                  {ROLES.map((r) => (
                    <button
                      key={r}
                      onClick={() => setRole(r)}
                      className={`px-4 py-2.5 rounded-xl border-2 font-medium transition-all duration-200 ${
                        role === r
                          ? 'border-primary bg-primary-pale text-primary shadow-sm'
                          : 'border-border-light hover:border-primary hover:bg-bg-soft text-text-primary'
                      }`}
                    >
                      {r}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <Input
                  type="text"
                  label="Topics of interest (comma-separated)"
                  value={topics}
                  onChange={(e) => setTopics(e.target.value)}
                  placeholder="e.g., GPT-4, Venture Capital, Product Design"
                />
              </div>
            </div>
          </div>

          {/* Email Settings */}
          <div className="bg-white rounded-xl p-8 shadow-md border border-border-light">
            <h2 className="text-xl font-semibold text-text-primary mb-4">
              Email Delivery
            </h2>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-text-primary mb-3">
                  Delivery time
                </label>
                <Input
                  type="time"
                  value={emailTime}
                  onChange={(e) => setEmailTime(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-primary mb-3">
                  Frequency
                </label>
                <div className="flex gap-3">
                  {['daily', 'weekly'].map((freq) => (
                    <button
                      key={freq}
                      onClick={() => setEmailFrequency(freq)}
                      className={`flex-1 px-4 py-3 rounded-xl border-2 font-medium transition-all duration-200 capitalize ${
                        emailFrequency === freq
                          ? 'border-primary bg-primary-pale text-primary shadow-sm'
                          : 'border-border-light hover:border-primary hover:bg-bg-soft text-text-primary'
                      }`}
                    >
                      {freq}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end gap-3">
            <Button
              variant="outline"
              onClick={() => navigate('/dashboard')}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleSave}
              disabled={saving || selectedIndustries.length === 0}
            >
              <Save className="h-4 w-4 mr-2" />
              {saving ? 'Saving...' : 'Save Preferences'}
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
};
