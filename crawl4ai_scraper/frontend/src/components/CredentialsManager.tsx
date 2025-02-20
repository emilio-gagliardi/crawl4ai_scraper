import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
  Alert,
  CircularProgress
} from '@mui/material';

interface Provider {
  provider_name: string;
  model_name: string;
  description: string;
}

interface Credentials {
  provider: string;
  model: string;
  provider_identifier: string;
}

const CredentialsManager: React.FC = () => {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [selectedProvider, setSelectedProvider] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [activeCredentials, setActiveCredentials] = useState<Credentials | null>(null);

  // Fetch available providers and active credentials on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [providersRes, activeRes] = await Promise.all([
          fetch('/api/credentials/providers'),
          fetch('/api/credentials/active')
        ]);

        if (providersRes.ok) {
          const providersData = await providersRes.json();
          setProviders(providersData);
        }

        if (activeRes.ok) {
          const activeData = await activeRes.json();
          setActiveCredentials(activeData);
          setSelectedProvider(activeData.provider);
          setSelectedModel(activeData.model);
        }
      } catch (err) {
        setError('Failed to fetch provider data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Get available models for selected provider
  const getModelsForProvider = (providerName: string): Provider[] => {
    return providers.filter(p => p.provider_name === providerName);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch('/api/credentials', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          provider_name: selectedProvider,
          model_name: selectedModel,
          api_key: apiKey
        })
      });

      if (!response.ok) {
        throw new Error('Failed to save credentials');
      }

      const data = await response.json();
      setSuccess('Credentials saved successfully');
      setActiveCredentials({
        provider: data.provider,
        model: data.model,
        provider_identifier: `${data.provider}/${data.model}`
      });
      setApiKey(''); // Clear sensitive data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !providers.length) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          LLM Provider Credentials
        </Typography>

        {activeCredentials && (
          <Alert severity="info" sx={{ mb: 2 }}>
            Active Provider: {activeCredentials.provider_identifier}
          </Alert>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <FormControl fullWidth margin="normal">
            <InputLabel>Provider</InputLabel>
            <Select
              value={selectedProvider}
              onChange={(e) => {
                setSelectedProvider(e.target.value);
                setSelectedModel('');
              }}
              required
            >
              {Array.from(new Set(providers.map(p => p.provider_name))).map(provider => (
                <MenuItem key={provider} value={provider}>
                  {provider}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth margin="normal">
            <InputLabel>Model</InputLabel>
            <Select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              disabled={!selectedProvider}
              required
            >
              {getModelsForProvider(selectedProvider).map(provider => (
                <MenuItem key={provider.model_name} value={provider.model_name}>
                  {provider.model_name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            fullWidth
            margin="normal"
            label="API Key"
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            required
            helperText="Your API key will be encrypted before storage"
          />

          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading}
            sx={{ mt: 2 }}
          >
            {loading ? <CircularProgress size={24} /> : 'Save Credentials'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default CredentialsManager; 