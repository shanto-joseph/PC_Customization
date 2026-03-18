/**
 * PC Builder Recommendation System
 * Provides intelligent component recommendations based on compatibility and performance matching
 */

class PCBuilderRecommendations {
    constructor() {
        this.compatibilityRules = {
            // CPU-Motherboard compatibility patterns
            cpuMotherboard: {
                intel: ['intel', 'lga', 'z690', 'z790', 'b660', 'b760', 'h610', 'h670'],
                amd: ['amd', 'am4', 'am5', 'b450', 'b550', 'x570', 'b650', 'x670']
            },
            
            // RAM-Motherboard compatibility
            ramMotherboard: {
                ddr4: ['ddr4', 'b450', 'b550', 'x570', 'z490', 'z590', 'b460', 'b560'],
                ddr5: ['ddr5', 'z690', 'z790', 'b660', 'b760', 'b650', 'x670']
            },
            
            // GPU power requirements (in watts)
            gpuPowerRequirements: {
                high: { keywords: ['rtx 4090', 'rx 7900 xtx', 'rtx 4080'], minWattage: 850 },
                midHigh: { keywords: ['rtx 4070', 'rtx 4080', 'rx 7800', 'rx 7900'], minWattage: 750 },
                mid: { keywords: ['rtx 4060', 'rtx 4070', 'rx 7600', 'rx 7700'], minWattage: 650 },
                budget: { keywords: ['rtx 4050', 'gtx 1660', 'rx 6500', 'rx 6600'], minWattage: 550 }
            },
            
            // CPU-GPU performance tiers
            cpuGpuTiers: {
                highEnd: {
                    cpus: ['i7', 'i9', 'ryzen 7', 'ryzen 9'],
                    gpus: ['rtx 4070', 'rtx 4080', 'rtx 4090', 'rx 7800', 'rx 7900']
                },
                midRange: {
                    cpus: ['i5', 'ryzen 5'],
                    gpus: ['rtx 4060', 'rtx 4070', 'rx 7600', 'rx 7700']
                },
                budget: {
                    cpus: ['i3', 'ryzen 3'],
                    gpus: ['rtx 4050', 'gtx 1660', 'rx 6500', 'rx 6600']
                }
            }
        };
    }

    // Main recommendation update function
    updateRecommendations(selectedComponents) {
        this.clearAllRecommendations();
        
        // Apply different recommendation strategies
        this.recommendCpuMotherboardCompatibility(selectedComponents);
        this.recommendRamCompatibility(selectedComponents);
        this.recommendGpuPerformanceMatch(selectedComponents);
        this.recommendPsuForGpu(selectedComponents);
        this.recommendCaseForMotherboard(selectedComponents);
        this.recommendBrandEcosystem(selectedComponents);
        this.recommendStorageForBuild(selectedComponents);
    }

    // Clear all existing recommendations
    clearAllRecommendations() {
        document.querySelectorAll('.recommendation-badge').forEach(badge => {
            badge.classList.add('d-none');
        });
        document.querySelectorAll('.component-card').forEach(card => {
            card.classList.remove('recommended');
        });
    }

    // CPU-Motherboard compatibility recommendations
    recommendCpuMotherboardCompatibility(selected) {
        if (!selected.cpu) return;

        const cpuName = selected.cpu.name.toLowerCase();
        const cpuBrand = selected.cpu.brand.toLowerCase();
        
        let compatibleKeywords = [];
        
        // Determine CPU type and get compatible motherboard keywords
        if (this.containsAny(cpuName + ' ' + cpuBrand, ['intel', 'i3', 'i5', 'i7', 'i9'])) {
            compatibleKeywords = this.compatibilityRules.cpuMotherboard.intel;
        } else if (this.containsAny(cpuName + ' ' + cpuBrand, ['amd', 'ryzen'])) {
            compatibleKeywords = this.compatibilityRules.cpuMotherboard.amd;
        }

        this.recommendComponentsByKeywords('motherboard', compatibleKeywords);
    }

    // RAM compatibility recommendations
    recommendRamCompatibility(selected) {
        if (!selected.motherboard) return;

        const mbName = selected.motherboard.name.toLowerCase();
        
        // Check for DDR4 compatibility
        if (this.containsAny(mbName, this.compatibilityRules.ramMotherboard.ddr4)) {
            this.recommendComponentsByKeywords('ram', ['ddr4']);
        }
        
        // Check for DDR5 compatibility
        if (this.containsAny(mbName, this.compatibilityRules.ramMotherboard.ddr5)) {
            this.recommendComponentsByKeywords('ram', ['ddr5']);
        }
    }

    // GPU performance matching recommendations
    recommendGpuPerformanceMatch(selected) {
        if (!selected.cpu) return;

        const cpuName = selected.cpu.name.toLowerCase();
        
        // Find CPU tier and recommend matching GPUs
        Object.entries(this.compatibilityRules.cpuGpuTiers).forEach(([tier, config]) => {
            if (this.containsAny(cpuName, config.cpus)) {
                this.recommendComponentsByKeywords('gpu', config.gpus);
            }
        });
    }

    // PSU recommendations based on GPU
    recommendPsuForGpu(selected) {
        if (!selected.gpu) return;

        const gpuName = selected.gpu.name.toLowerCase();
        
        Object.entries(this.compatibilityRules.gpuPowerRequirements).forEach(([tier, config]) => {
            if (this.containsAny(gpuName, config.keywords)) {
                const wattageKeywords = [`${config.minWattage}w`, `${config.minWattage + 100}w`, `${config.minWattage + 200}w`];
                this.recommendComponentsByKeywords('psu', wattageKeywords);
            }
        });
    }

    // Case recommendations based on motherboard form factor
    recommendCaseForMotherboard(selected) {
        if (!selected.motherboard) return;

        const mbName = selected.motherboard.name.toLowerCase();
        
        if (mbName.includes('atx') && !mbName.includes('mini') && !mbName.includes('micro')) {
            this.recommendComponentsByKeywords('case', ['atx', 'full tower', 'mid tower']);
        } else if (this.containsAny(mbName, ['micro', 'matx', 'mini'])) {
            this.recommendComponentsByKeywords('case', ['micro', 'mini', 'compact']);
        }
    }

    // Brand ecosystem recommendations
    recommendBrandEcosystem(selected) {
        const selectedBrands = this.getSelectedBrands(selected);
        
        // Recommend components from same premium brands for unselected components
        ['ram', 'storage', 'psu', 'case'].forEach(componentType => {
            if (!selected[componentType]) {
                document.querySelectorAll(`[data-component="${componentType}"]`).forEach(card => {
                    const brand = card.dataset.brand.toLowerCase();
                    
                    if (selectedBrands.some(selectedBrand => 
                        this.areBrandsCompatible(selectedBrand, brand))) {
                        this.showRecommendation(card);
                    }
                });
            }
        });
    }

    // Storage recommendations based on build tier
    recommendStorageForBuild(selected) {
        if (!selected.cpu && !selected.gpu) return;

        const buildTier = this.determineBuildTier(selected);
        
        let storageKeywords = [];
        switch (buildTier) {
            case 'high':
                storageKeywords = ['nvme', 'ssd', '1tb', '2tb', 'gen4'];
                break;
            case 'mid':
                storageKeywords = ['ssd', 'nvme', '500gb', '1tb'];
                break;
            case 'budget':
                storageKeywords = ['ssd', '256gb', '500gb'];
                break;
        }
        
        this.recommendComponentsByKeywords('storage', storageKeywords);
    }

    // Helper functions
    containsAny(text, keywords) {
        return keywords.some(keyword => text.includes(keyword.toLowerCase()));
    }

    recommendComponentsByKeywords(componentType, keywords) {
        document.querySelectorAll(`[data-component="${componentType}"]`).forEach(card => {
            const name = card.dataset.name.toLowerCase();
            const brand = card.dataset.brand.toLowerCase();
            
            if (this.containsAny(name + ' ' + brand, keywords)) {
                this.showRecommendation(card);
            }
        });
    }

    getSelectedBrands(selected) {
        const brands = [];
        Object.values(selected).forEach(component => {
            if (component && component.brand) {
                brands.push(component.brand.toLowerCase());
            }
        });
        return brands;
    }

    areBrandsCompatible(brand1, brand2) {
        const premiumBrands = ['asus', 'msi', 'corsair', 'gigabyte', 'evga', 'seasonic'];
        return premiumBrands.includes(brand1) && premiumBrands.includes(brand2);
    }

    determineBuildTier(selected) {
        let tier = 'budget';
        
        if (selected.cpu) {
            const cpuName = selected.cpu.name.toLowerCase();
            if (this.containsAny(cpuName, ['i7', 'i9', 'ryzen 7', 'ryzen 9'])) {
                tier = 'high';
            } else if (this.containsAny(cpuName, ['i5', 'ryzen 5'])) {
                tier = 'mid';
            }
        }
        
        if (selected.gpu) {
            const gpuName = selected.gpu.name.toLowerCase();
            if (this.containsAny(gpuName, ['rtx 4080', 'rtx 4090', 'rx 7900'])) {
                tier = 'high';
            } else if (this.containsAny(gpuName, ['rtx 4070', 'rx 7800'])) {
                tier = tier === 'budget' ? 'mid' : tier;
            }
        }
        
        return tier;
    }

    showRecommendation(card) {
        const badge = card.querySelector('.recommendation-badge');
        if (badge) {
            badge.classList.remove('d-none');
            card.classList.add('recommended');
        }
    }
}

// Export for use in main template
window.PCBuilderRecommendations = PCBuilderRecommendations;