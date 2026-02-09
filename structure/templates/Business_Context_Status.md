
{
  "phaseId": "03-business-context-discovery",
  "phaseName": "Business Context Discovery (Phase 3.0)",
  "status": "in_progress",
  "lastUpdated": "YYYY-MM-DDTHH:MM:SSZ",
  "totalWorkpackages": 0,
  "completedWorkpackages": 0,
  "inProgressWorkpackages": 0,
  "pendingWorkpackages": 0,
  "failedWorkpackages": 0,
  "progressPercentage": 0,
  
  "workpackages": [
    {
      "workpackageId": "WP-001",
      "workpackageName": "Example Workpackage",
      "priority": 1,
      "status": "completed",
      "businessContextDocument": "output/business_specification/context/WP-001-business-context.md",
      "completedDate": "YYYY-MM-DDTHH:MM:SSZ",
      "confidenceLevel": "High",
      "confidenceRationale": "Clear business domain, well-documented stakeholders, comprehensive vocabulary",
      
      "businessDomain": {
        "primaryDomain": "Order Management",
        "subDomain": "Order Validation",
        "confidence": "High"
      },
      
      "businessStakeholders": {
        "primaryUsers": ["Customer Service Representatives", "Order Processing Team"],
        "businessOwners": ["Order Management Department"],
        "otherStakeholders": ["Finance Team", "Warehouse Team"],
        "documented": true
      },
      
      "businessVocabulary": {
        "entitiesIdentified": 5,
        "attributesIdentified": 15,
        "termsExtracted": 20,
        "glossaryUpdated": true
      },
      
      "businessConstraints": {
        "rulesIdentified": 8,
        "policiesIdentified": 3,
        "constraintsIdentified": 2
      },
      
      "businessOutcomes": {
        "primaryOutcome": "Enable efficient order validation and processing",
        "businessValue": "Reduce order processing time by 50%",
        "documented": true
      },
      
      "clarificationsNeeded": [
        "Confirm credit limit calculation logic with Finance team",
        "Verify order approval workflow with Business Owner"
      ],
      
      "errors": [],
      "lastUpdated": "YYYY-MM-DDTHH:MM:SSZ"
    }
  ],
  
  "businessGlossary": {
    "glossaryPath": "output/business_specification/context/business-glossary.md",
    "totalTerms": 0,
    "lastUpdated": "YYYY-MM-DDTHH:MM:SSZ",
    "termsByDomain": {
      "Order Management": 20,
      "Customer Service": 15,
      "Billing": 10
    }
  },
  
  "issuesAndBlockers": [
    {
      "workpackageId": "WP-002",
      "issueType": "Ambiguous Business Domain",
      "description": "Unable to determine primary business domain from code",
      "status": "open",
      "resolution": "Awaiting business stakeholder input",
      "createdDate": "YYYY-MM-DDTHH:MM:SSZ"
    }
  ]
}

