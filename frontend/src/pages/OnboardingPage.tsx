import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Check } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { Logo } from '../components/common/Logo';
import { api } from '../lib/api';

type Step = 1 | 2 | 3 | 4;

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

export const OnboardingPage: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState<Step>(1);
  const [loading, setLoading] = useState(false);

  // Step 1: Industries
  const [selectedIndustries, setSelectedIndustries] = useState<string[]>([]);

  // Step 2: Companies
  const [companyInput, setCompanyInput] = useState('');
  const [companies, setCompanies] = useState<string[]>([]);

  // Step 3: Role and Topics
  const [role, setRole] = useState('');
  const [topics, setTopics] = useState('');

  // Step 4: Email preferences
  const [emailTime, setEmailTime] = useState('08:00');
  const [emailFrequency, setEmailFrequency] = useState('daily');

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

  const handleNext = () => {
    if (step < 4) {
      setStep((prev) => (prev + 1) as Step);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep((prev) => (prev - 1) as Step);
    }
  };

  const handleComplete = async () => {
    setLoading(true);
    try {
      await api.updatePreferences({
        industries: selectedIndustries,
        companies_to_track: companies,
        role,
        topics_of_interest: topics.split(',').map((t) => t.trim()),
        email_time: emailTime,
        email_frequency: emailFrequency,
      });
      navigate('/dashboard');
    } catch (error) {
      console.error('Failed to save preferences:', error);
    } finally {
      setLoading(false);
    }
  };

  const canProceed = () => {
    switch (step) {
      case 1:
        return selectedIndustries.length > 0;
      case 2:
        return true; // Optional step
      case 3:
        return role !== '';
      case 4:
        return true;
      default:
        return false;
    }
  };

  return (
    <div className="min-h-screen gradient-purple flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl p-8 max-w-2xl w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <Logo className="justify-center mb-4" />
          <h1 className="text-3xl font-bold text-text-primary mb-2">
            Welcome to UP2D8!
          </h1>
          <p className="text-text-secondary">
            Let's personalize your daily digest
          </p>
        </div>

        {/* Progress indicator */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {[1, 2, 3, 4].map((s) => (
            <div
              key={s}
              className={`h-2 w-12 rounded-full transition-colors ${
                s === step
                  ? 'bg-primary'
                  : s < step
                  ? 'bg-primary-light'
                  : 'bg-border-light'
              }`}
            />
          ))}
        </div>

        {/* Step content */}
        <div className="mb-8">
          {step === 1 && (
            <div>
              <h2 className="text-2xl font-semibold text-text-primary mb-2">
                Which industries interest you?
              </h2>
              <p className="text-text-secondary mb-6">
                Select all that apply
              </p>
              <div className="flex flex-wrap gap-3">
                {INDUSTRIES.map((industry) => (
                  <button
                    key={industry}
                    onClick={() => toggleIndustry(industry)}
                    className={`px-4 py-2 rounded-lg border-2 transition-colors ${
                      selectedIndustries.includes(industry)
                        ? 'border-primary bg-primary-pale text-primary font-semibold'
                        : 'border-border-light hover:border-primary'
                    }`}
                  >
                    {industry}
                  </button>
                ))}
              </div>
            </div>
          )}

          {step === 2 && (
            <div>
              <h2 className="text-2xl font-semibold text-text-primary mb-2">
                Any specific companies to track?
              </h2>
              <p className="text-text-secondary mb-6">
                We'll prioritize news about these companies (optional)
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
          )}

          {step === 3 && (
            <div>
              <h2 className="text-2xl font-semibold text-text-primary mb-2">
                Tell us about yourself
              </h2>
              <p className="text-text-secondary mb-6">
                This helps us personalize your content
              </p>
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
                        className={`px-4 py-2 rounded-lg border-2 transition-colors ${
                          role === r
                            ? 'border-primary bg-primary-pale text-primary font-semibold'
                            : 'border-border-light hover:border-primary'
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
                    label="Specific topics you care about (comma-separated)"
                    value={topics}
                    onChange={(e) => setTopics(e.target.value)}
                    placeholder="e.g., GPT-4, Venture Capital, Product Design"
                  />
                </div>
              </div>
            </div>
          )}

          {step === 4 && (
            <div>
              <h2 className="text-2xl font-semibold text-text-primary mb-2">
                Email preferences
              </h2>
              <p className="text-text-secondary mb-6">
                When should we send your digest?
              </p>
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
                        className={`flex-1 px-4 py-3 rounded-lg border-2 transition-colors capitalize ${
                          emailFrequency === freq
                            ? 'border-primary bg-primary-pale text-primary font-semibold'
                            : 'border-border-light hover:border-primary'
                        }`}
                      >
                        {freq}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Navigation buttons */}
        <div className="flex gap-3">
          {step > 1 && (
            <Button variant="outline" onClick={handleBack} className="flex-1">
              Back
            </Button>
          )}
          {step < 4 ? (
            <Button
              variant="primary"
              onClick={handleNext}
              disabled={!canProceed()}
              className="flex-1"
            >
              Next
            </Button>
          ) : (
            <Button
              variant="primary"
              onClick={handleComplete}
              disabled={!canProceed() || loading}
              className="flex-1"
            >
              {loading ? 'Saving...' : 'Complete Setup'}
            </Button>
          )}
        </div>

        {/* Skip option */}
        {step === 1 && (
          <div className="text-center mt-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="text-sm text-text-secondary hover:text-primary"
            >
              Skip for now
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
