#!/bin/bash

# 🏛️ Enhanced Cardano Agent Demo - Quick Runner
# Complete AI Agent Economy Demonstration
#
# Usage:
#   ./run_cardano_demo.sh                    # Full demo
#   ./run_cardano_demo.sh register_agent     # Agent registration only
#   ./run_cardano_demo.sh service_marketplace # Service marketplace only
#   ./run_cardano_demo.sh revenue_sharing    # Revenue sharing only
#   ./run_cardano_demo.sh cross_chain        # Cross-chain operations only
#   ./run_cardano_demo.sh compliance         # Compliance framework only

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Demo header
echo -e "${BLUE}🏛️ Enhanced Cardano Agent Demo${NC}"
echo -e "${BLUE}=================================${NC}"
echo

# Check if we're in the right directory
if [ ! -f "examples/cardano_enhanced_agent.py" ]; then
    echo -e "${RED}❌ Error: Please run this script from the agent_forge root directory${NC}"
    echo -e "${YELLOW}💡 Solution: cd agent_forge && ./run_cardano_demo.sh${NC}"
    exit 1
fi

# Check Python availability
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Error: Python not found${NC}"
    echo -e "${YELLOW}💡 Solution: Install Python 3.8+ and try again${NC}"
    exit 1
fi

# Check if Enhanced Cardano Agent is available
echo -e "${BLUE}🔍 Checking Enhanced Cardano Agent availability...${NC}"
if python -c "from examples.cardano_enhanced_agent import CardanoEnhancedAgent" 2>/dev/null; then
    echo -e "${GREEN}✅ Enhanced Cardano Agent available${NC}"
else
    echo -e "${RED}❌ Enhanced Cardano Agent not found${NC}"
    echo -e "${YELLOW}💡 Solution: Ensure Agent Forge is properly setup${NC}"
    exit 1
fi

# Determine operation
OPERATION=${1:-full_demo}

echo -e "${BLUE}🎯 Running operation: ${OPERATION}${NC}"
echo

# Validate operation
case $OPERATION in
    full_demo|register_agent|service_marketplace|revenue_sharing|cross_chain|compliance)
        ;;
    *)
        echo -e "${RED}❌ Invalid operation: $OPERATION${NC}"
        echo -e "${YELLOW}💡 Valid operations: full_demo, register_agent, service_marketplace, revenue_sharing, cross_chain, compliance${NC}"
        exit 1
        ;;
esac

# Run the demo
echo -e "${GREEN}🚀 Starting Enhanced Cardano Agent Demo...${NC}"
echo

if python tools/demos/cardano_enhanced_demo.py --operation "$OPERATION"; then
    echo
    echo -e "${GREEN}🎉 Demo completed successfully!${NC}"
    echo -e "${BLUE}📚 Learn more: docs/integrations/CARDANO_IMPLEMENTATION_COMPLETE.md${NC}"
else
    echo
    echo -e "${RED}❌ Demo failed${NC}"
    echo -e "${YELLOW}💡 Check troubleshooting guide: tools/demos/README.md${NC}"
    exit 1
fi