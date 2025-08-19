import React, { useState, useEffect } from 'react';
import { apiClient } from '../utils/apiClient';
import type { VersionResponse } from '../utils/apiClient';

export function VersionFooter() {
	const [version, setVersion] = useState<VersionResponse | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		async function fetchVersion() {
			try {
				setLoading(true);
				const data = await apiClient.getVersion();
				setVersion(data);
				setError(null);
			} catch (err) {
				console.error('Failed to fetch version:', err);
				setError('Version info unavailable');
				// Use fallback version
				setVersion({
					version: '2.0.0',
					commit: 'unknown',
					environment: 'production',
					deployment_date: new Date().toISOString(),
					build_number: 'fallback'
				});
			} finally {
				setLoading(false);
			}
		}

		fetchVersion();
	}, []);

	if (loading) {
		return (
			<div className="fixed bottom-0 left-0 right-0 bg-[#0B0D12]/80 backdrop-blur-sm border-t border-white/8 px-4 py-2">
				<div className="container mx-auto flex items-center justify-between text-xs text-[#A7B3C5]">
					<div className="animate-pulse">Loading version...</div>
				</div>
			</div>
		);
	}

	if (!version) {
		return null;
	}

	// Format deployment date
	const deploymentDate = version.deployment_date 
		? new Date(version.deployment_date).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		})
		: 'Unknown';

	// Determine environment color
	const envColor = {
		production: 'text-green-400',
		staging: 'text-yellow-400',
		development: 'text-blue-400'
	}[version.environment] || 'text-gray-400';

	// Create changelog link
	const changelogLink = version.commit && version.commit !== 'unknown' 
		? `https://github.com/user/SPY-tracker/commit/${version.commit.substring(0, 7)}`
		: '#';

	return (
		<div className="fixed bottom-0 left-0 right-0 bg-[#0B0D12]/80 backdrop-blur-sm border-t border-white/8 px-4 py-2 z-40">
			<div className="container mx-auto flex items-center justify-between text-xs">
				<div className="flex items-center gap-4">
					<span className="text-[#A7B3C5]">
						SPY TA Tracker v{version.version}
					</span>
					{version.commit !== 'unknown' && (
						<a 
							href={changelogLink}
							target="_blank"
							rel="noopener noreferrer"
							className="text-[#006072] hover:text-[#0080A0] transition-colors"
							title="View commit on GitHub"
						>
							{version.commit.substring(0, 7)}
						</a>
					)}
					<span className={`${envColor} font-medium`}>
						{version.environment.toUpperCase()}
					</span>
				</div>
				<div className="flex items-center gap-4 text-[#A7B3C5]">
					{error && (
						<span className="text-yellow-400 text-xs">
							⚠️ {error}
						</span>
					)}
					<span title="Deployment date">
						Deployed: {deploymentDate}
					</span>
					{version.build_number !== 'fallback' && (
						<span title="Build number">
							Build #{version.build_number}
						</span>
					)}
				</div>
			</div>
		</div>
	);
}