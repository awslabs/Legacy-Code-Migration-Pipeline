# Phase 4.3: Batch Code Generation

---

## Orchestration Information

**Phase**: Phase 4 - Code Generation
**Step**: Step 4.3 - Batch Code Generation
**Team Supervisor**: code_generation_team_supervisor
**Assigned Agent**: code_generation_specialist_batch
**Task File Name**: {{TASKS_BASE_PATH}}/phase_4.3_batch_generation.md

### Expected Deliverables

1. **Job Configuration Implementation**
   - Location: {{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}/config/
   - Description: Batch job configuration and definitions
   - Includes: Job definitions, step configurations, scheduling

2. **Reader Implementation**
   - Location: {{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}/reader/
   - Description: Data readers for batch processing
   - Includes: Database readers, file readers, custom readers

3. **Processor Implementation**
   - Location: {{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}/processor/
   - Description: Business logic processors
   - Includes: Item processors, validation, transformation logic

4. **Writer Implementation**
   - Location: {{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}/writer/
   - Description: Data writers for batch output
   - Includes: Database writers, file writers, custom writers

5. **Error Handling and Recovery Implementation**
   - Location: {{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}/error/
   - Description: Error handling, skip logic, retry mechanisms
   - Includes: Skip listeners, retry policies, error handlers

6. **Progress Tracking Update**
   - File: {{CODE_GENERATION_STATUS}}
   - Description: Updated progress with batch completion for this workpackage

7. **Error Reports** (if applicable)
   - File: {{CODE_GENERATION_ERRORS}}
   - Description: Documentation of issues encountered during generation

### Success Criteria
- [ ] All batch jobs configured correctly
- [ ] All readers implemented with proper data access
- [ ] All processors implemented with business logic
- [ ] All writers implemented with proper output handling
- [ ] Error handling and retry logic implemented
- [ ] Restart/recovery capability implemented
- [ ] Code compiles without errors
- [ ] All business rules traceable to business specification
- [ ] Proper batch patterns followed
- [ ] Transaction management implemented
- [ ] Chunk size and commit intervals configured
- [ ] Progress tracking updated with batch completion
- [ ] All deliverables produced at specified paths
- [ ] Ready for next workpackage

---

## Context

### Workpackage Context (Provided at Runtime)
- **Workpackage ID**: WP-{ID} (e.g., WP-001)
- **Workpackage Name**: [Name from workpackage planning]
- **Workpackage Description**: [Description from business specification]

### Input Locations
- **Business specification**: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification.md`
- **Test case specification**: `{{TEST_GENERATION_DOMAIN_BASE_PATH}}/WP-{ID}-tests.md`
- **Target batch specification**: `{{TARGET_SPECIFICATION}}/03-BATCH-SPECIFICATION.md`
- **Batch sample code**: `{{TARGET_SAMPLE_CODE}}/batch/`
- **Project structure**: `{{CODE_GENERATION_BATCH_OUTPUT}}/` (from Phase 4.0)

### Output Locations
- **Batch code**: `{{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}/`
- **Progress tracking**: `{{CODE_GENERATION_STATUS}}`
- **Error reports**: `{{CODE_GENERATION_ERRORS}}`

### Previous Phase Artifacts
- **From Phase 4.0**: Project structure, build configuration, configuration templates
- **From Phase 3**: Business specification with detailed requirements
- **From Phase 3**: Test case definitions

---

## Objective

Implement the batch tier for the specified workpackage, translating business requirements from the business specification into working batch code that follows the target batch specification's architecture, patterns, and conventions.

**CRITICAL**: This phase implements ONE workpackage only. Focus exclusively on the batch processing requirements, business rules, and data flows defined in the workpackage's business specification. Do not implement functionality from other workpackages.

---

## Instructions

### 1. Preparation

#### 1.1 Read Business Specification
1. Open and read `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification.md`
2. Extract key information:
   - **Batch Processing Requirements**: What data needs to be processed in batch
   - **Business Rules**: All business logic that must be implemented
   - **Data Sources**: Input data sources (database, files, APIs)
   - **Data Transformations**: How data should be transformed
   - **Data Destinations**: Output destinations (database, files, APIs)
   - **Validation Rules**: Data validation requirements
   - **Error Handling**: How errors should be handled
   - **Scheduling Requirements**: When and how often jobs should run
   - **Performance Requirements**: Volume, throughput, timing constraints

3. Identify implementation scope:
   - Which batch jobs need to be created
   - Which business rules need to be implemented
   - Which data sources need to be read
   - Which transformations need to be applied
   - Which outputs need to be written
   - Which error scenarios need to be handled

#### 1.2 Read Target Batch Specification
1. Open and read `{{TARGET_SPECIFICATION}}/03-BATCH-SPECIFICATION.md`
2. Extract implementation guidance:
   - **Framework**: Spring Batch, Jakarta Batch, custom framework
   - **Architecture Pattern**: Job/Step/Tasklet patterns
   - **Naming Conventions**: Job, step, bean naming rules
   - **Chunk Processing**: Chunk size, commit intervals
   - **Transaction Management**: Transaction boundaries, propagation
   - **Error Handling**: Skip policies, retry policies, error handlers
   - **Restart/Recovery**: Restart capabilities, state management
   - **Job Parameters**: Parameter passing and validation
   - **Listeners**: Job/step/chunk listeners for monitoring
   - **Scheduling**: Scheduling mechanisms (Quartz, cron, etc.)

3. Review sample code at `{{TARGET_SAMPLE_CODE}}/batch/` for:
   - Job configuration examples
   - Reader implementation examples
   - Processor implementation examples
   - Writer implementation examples
   - Error handling examples
   - Restart/recovery examples

#### 1.3 Read Test Case Specification
1. Open and read `{{TEST_GENERATION_DOMAIN_BASE_PATH}}/WP-{ID}-tests.md`
2. Extract test requirements:
   - Test scenarios that must be supported
   - Edge cases that must be handled
   - Error scenarios
   - Volume/performance requirements

### 2. Job Configuration Implementation

#### 2.1 Identify Job Requirements
From the business specification, identify:
- What batch jobs are needed
- What steps each job contains
- What the execution flow is (sequential, parallel, conditional)
- What job parameters are needed
- What scheduling is required

#### 2.2 Implement Job Configuration
For each batch job in the business specification:

1. **Create Job Configuration Class**
   - Location: `{{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}/config/[JobName]Config.java`
   - Follow naming conventions from batch specification
   - Use appropriate annotations (@Configuration, @EnableBatchProcessing)
   - Reference batch specification for configuration patterns

**Example Structure** (Spring Batch):
```java
@Configuration
@EnableBatchProcessing
public class EntityProcessingJobConfig {
    
    @Autowired
    private JobBuilderFactory jobBuilderFactory;
    
    @Autowired
    private StepBuilderFactory stepBuilderFactory;
    
    @Bean
    public Job entityProcessingJob(
            Step readAndProcessStep,
            Step validationStep,
            Step writeStep) {
        return jobBuilderFactory.get("entityProcessingJob")
            .incrementer(new RunIdIncrementer())
            .start(readAndProcessStep)
            .next(validationStep)
            .next(writeStep)
            .listener(jobExecutionListener())
            .build();
    }
    
    @Bean
    public Step readAndProcessStep(
            ItemReader<EntityInput> reader,
            ItemProcessor<EntityInput, EntityOutput> processor,
            ItemWriter<EntityOutput> writer) {
        return stepBuilderFactory.get("readAndProcessStep")
            .<EntityInput, EntityOutput>chunk(100)
            .reader(reader)
            .processor(processor)
            .writer(writer)
            .faultTolerant()
            .skipLimit(10)
            .skip(ValidationException.class)
            .retryLimit(3)
            .retry(TransientException.class)
            .listener(stepExecutionListener())
            .build();
    }
    
    @Bean
    public JobExecutionListener jobExecutionListener() {
        return new EntityProcessingJobListener();
    }
    
    @Bean
    public StepExecutionListener stepExecutionListener() {
        return new EntityProcessingStepListener();
    }
}
```

#### 2.3 Configure Job Parameters
Define job parameters for runtime configuration:
- Input file paths or database queries
- Processing dates or date ranges
- Batch size or chunk size
- Output destinations
- Processing modes (full, incremental, delta)

**Example**:
```java
@Bean
@StepScope
public FlatFileItemReader<EntityInput> reader(
        @Value("#{jobParameters['inputFile']}") String inputFile) {
    return new FlatFileItemReaderBuilder<EntityInput>()
        .name("entityReader")
        .resource(new FileSystemResource(inputFile))
        .delimited()
        .names(new String[]{"id", "name", "value"})
        .fieldSetMapper(new BeanWrapperFieldSetMapper<>() {{
            setTargetType(EntityInput.class);
        }})
        .build();
}
```

#### 2.4 Validate Job Configuration
- [ ] All jobs from business specification are configured
- [ ] Job steps are defined correctly
- [ ] Execution flow matches business requirements
- [ ] Job parameters are defined
- [ ] Listeners are configured for monitoring
- [ ] Code follows batch specification conventions

### 3. Reader Implementation

#### 3.1 Identify Reader Requirements
From the business specification, identify:
- What data sources need to be read (database, files, APIs)
- What data format is expected (CSV, XML, JSON, database records)
- What filtering or selection criteria apply
- What volume of data is expected

#### 3.2 Implement Database Readers
For database data sources:

1. **Create Repository Reader**
   - Location: `{{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}/reader/[EntityName]RepositoryReader.java`
   - Use JpaPagingItemReader or JdbcPagingItemReader
   - Configure page size based on batch specification
   - Add appropriate SQL queries or JPA queries

**Example Structure** (Spring Batch with JPA):
```java
@Configuration
public class EntityRepositoryReaderConfig {
    
    @Autowired
    private EntityManagerFactory entityManagerFactory;
    
    @Bean
    @StepScope
    public JpaPagingItemReader<Entity> entityReader(
            @Value("#{jobParameters['processingDate']}") String processingDate) {
        
        JpaPagingItemReader<Entity> reader = new JpaPagingItemReader<>();
        reader.setEntityManagerFactory(entityManagerFactory);
        reader.setQueryString(
            "SELECT e FROM Entity e WHERE e.processingDate = :processingDate " +
            "AND e.status = 'PENDING' ORDER BY e.id"
        );
        reader.setParameterValues(Collections.singletonMap("processingDate", processingDate));
        reader.setPageSize(100);
        
        return reader;
    }
}
```

#### 3.3 Implement File Readers
For file data sources:

1. **Create File Reader**
   - Location: `{{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}/reader/[EntityName]FileReader.java`
   - Use FlatFileItemReader for CSV/delimited files
   - Use StaxEventItemReader for XML files
   - Use JsonItemReader for JSON files
   - Configure field mappings

**Example Structure** (CSV File Reader):
```java
@Configuration
public class EntityFileReaderConfig {
    
    @Bean
    @StepScope
    public FlatFileItemReader<EntityInput> entityFileReader(
            @Value("#{jobParameters['inputFile']}") String inputFile) {
        
        return new FlatFileItemReaderBuilder<EntityInput>()
            .name("entityFileReader")
            .resource(new FileSystemResource(inputFile))
            .delimited()
            .delimiter(",")
            .names(new String[]{"id", "name", "value", "status"})
            .linesToSkip(1) // Skip header
            .fieldSetMapper(new BeanWrapperFieldSetMapper<>() {{
                setTargetType(EntityInput.class);
            }})
            .build();
    }
}
```

#### 3.4 Implement Custom Readers
For complex data sources (APIs, multiple sources, etc.):

1. **Create Custom Reader**
   - Location: `{{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}/reader/[EntityName]CustomReader.java`
   - Implement ItemReader interface
   - Implement read() method
   - Handle pagination or iteration logic
   - Manage state for restart capability

**Example Structure**:
```java
public class EntityApiReader implements ItemReader<EntityInput> {
    
    private final RestTemplate restTemplate;
    private final String apiUrl;
    private int currentPage = 0;
    private List<EntityInput> currentBatch;
    private int currentIndex = 0;
    
    public EntityApiReader(RestTemplate restTemplate, String apiUrl) {
        this.restTemplate = restTemplate;
        this.apiUrl = apiUrl;
    }
    
    @Override
    public EntityInput read() throws Exception {
        if (currentBatch == null || currentIndex >= currentBatch.size()) {
            currentBatch = fetchNextBatch();
            currentIndex = 0;
            
            if (currentBatch == null || currentBatch.isEmpty()) {
                return null; // End of data
            }
        }
        
        return currentBatch.get(currentIndex++);
    }
    
    private List<EntityInput> fetchNextBatch() {
        // Fetch data from API
        String url = apiUrl + "?page=" + currentPage + "&size=100";
        EntityInputPage page = restTemplate.getForObject(url, EntityInputPage.class);
        currentPage++;
        return page != null ? page.getContent() : Collections.emptyList();
    }
}
```

#### 3.5 Validate Readers
- [ ] All data sources are read correctly
- [ ] Data format parsing is correct
- [ ] Filtering/selection criteria are applied
- [ ] Pagination is implemented for large datasets
- [ ] Readers follow batch specification patterns

### 4. Processor Implementation

#### 4.1 Identify Processor Requirements
From the business specification, identify:
- What business logic needs to be applied
- What transformations are needed
- What validations must be performed
- What enrichment or lookups are required
- What business rules must be enforced

#### 4.2 Implement Item Processors
For each processing requirement:

1. **Create Processor Class**
   - Location: `{{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}/processor/[EntityName]Processor.java`
   - Implement ItemProcessor interface
   - Implement business logic in process() method
   - Add validation logic
   - Add transformation logic
   - Reference batch specification for processor patterns

**Example Structure**:
```java
@Component
public class EntityProcessor implements ItemProcessor<EntityInput, EntityOutput> {
    
    private final EntityService entityService;
    private final ValidationService validationService;
    
    public EntityProcessor(EntityService entityService, ValidationService validationService) {
        this.entityService = entityService;
        this.validationService = validationService;
    }
    
    @Override
    public EntityOutput process(EntityInput input) throws Exception {
        // Business rule: BR-001 - Validate input data
        if (!validationService.isValid(input)) {
            throw new ValidationException("Invalid input: " + input.getId());
        }
        
        // Business rule: BR-002 - Transform data
        EntityOutput output = new EntityOutput();
        output.setId(input.getId());
        output.setName(input.getName().toUpperCase());
        output.setValue(calculateValue(input));
        
        // Business rule: BR-003 - Enrich with additional data
        enrichWithReferenceData(output);
        
        // Business rule: BR-004 - Apply business logic
        applyBusinessRules(output);
        
        return output;
    }
    
    private double calculateValue(EntityInput input) {
        // Business calculation logic
        return input.getValue() * 1.1; // Example: 10% markup
    }
    
    private void enrichWithReferenceData(EntityOutput output) {
        // Lookup and add reference data
        ReferenceData refData = entityService.getReferenceData(output.getId());
        output.setCategory(refData.getCategory());
        output.setRegion(refData.getRegion());
    }
    
    private void applyBusinessRules(EntityOutput output) {
        // Business rule: BR-005 - Status determination
        if (output.getValue() > 1000) {
            output.setStatus("HIGH_VALUE");
        } else if (output.getValue() > 100) {
            output.setStatus("MEDIUM_VALUE");
        } else {
            output.setStatus("LOW_VALUE");
        }
        
        // Business rule: BR-006 - Flag for review
        if (output.getValue() > 10000) {
            output.setRequiresReview(true);
        }
    }
}
```

#### 4.3 Implement Composite Processors
For complex processing pipelines:

1. **Create Composite Processor**
   - Chain multiple processors together
   - Each processor handles one aspect of processing
   - Follow single responsibility principle

**Example Structure**:
```java
@Configuration
public class EntityProcessorConfig {
    
    @Bean
    public CompositeItemProcessor<EntityInput, EntityOutput> compositeProcessor() {
        CompositeItemProcessor<EntityInput, EntityOutput> processor = 
            new CompositeItemProcessor<>();
        
        List<ItemProcessor<?, ?>> delegates = new ArrayList<>();
        delegates.add(validationProcessor());
        delegates.add(transformationProcessor());
        delegates.add(enrichmentProcessor());
        delegates.add(businessRuleProcessor());
        
        processor.setDelegates(delegates);
        return processor;
    }
    
    @Bean
    public ItemProcessor<EntityInput, EntityInput> validationProcessor() {
        return new ValidationProcessor();
    }
    
    @Bean
    public ItemProcessor<EntityInput, EntityIntermediate> transformationProcessor() {
        return new TransformationProcessor();
    }
    
    @Bean
    public ItemProcessor<EntityIntermediate, EntityIntermediate> enrichmentProcessor() {
        return new EnrichmentProcessor();
    }
    
    @Bean
    public ItemProcessor<EntityIntermediate, EntityOutput> businessRuleProcessor() {
        return new BusinessRuleProcessor();
    }
}
```

#### 4.4 Implement Filtering Processors
For conditional processing:

1. **Return null to filter out items**
   - Items that return null are not passed to writer
   - Use for conditional processing

**Example**:
```java
@Component
public class EntityFilterProcessor implements ItemProcessor<EntityInput, EntityOutput> {
    
    @Override
    public EntityOutput process(EntityInput input) throws Exception {
        // Business rule: BR-007 - Only process active entities
        if (!"ACTIVE".equals(input.getStatus())) {
            return null; // Filter out inactive entities
        }
        
        // Business rule: BR-008 - Only process entities within date range
        if (input.getDate().isBefore(LocalDate.now().minusDays(30))) {
            return null; // Filter out old entities
        }
        
        // Process and return
        EntityOutput output = new EntityOutput();
        // ... transformation logic
        return output;
    }
}
```

#### 4.5 Validate Processors
- [ ] All business logic is implemented
- [ ] All transformations are correct
- [ ] All validations are enforced
- [ ] Business rules are traceable (comments with rule IDs)
- [ ] Processors follow batch specification patterns
- [ ] Error scenarios are handled appropriately

### 5. Writer Implementation

#### 5.1 Identify Writer Requirements
From the business specification, identify:
- What data destinations are needed (database, files, APIs)
- What data format is required (CSV, XML, JSON, database records)
- What transaction boundaries apply
- What error handling is needed for write failures

#### 5.2 Implement Database Writers
For database destinations:

1. **Create Repository Writer**
   - Location: `{{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}/writer/[EntityName]RepositoryWriter.java`
   - Use JpaItemWriter or JdbcBatchItemWriter
   - Configure batch size for optimal performance
   - Handle constraint violations

**Example Structure** (Spring Batch with JPA):
```java
@Configuration
public class EntityRepositoryWriterConfig {
    
    @Autowired
    private EntityManagerFactory entityManagerFactory;
    
    @Bean
    public JpaItemWriter<EntityOutput> entityWriter() {
        JpaItemWriter<EntityOutput> writer = new JpaItemWriter<>();
        writer.setEntityManagerFactory(entityManagerFactory);
        return writer;
    }
}
```

**Example with JDBC**:
```java
@Configuration
public class EntityJdbcWriterConfig {
    
    @Autowired
    private DataSource dataSource;
    
    @Bean
    public JdbcBatchItemWriter<EntityOutput> entityJdbcWriter() {
        return new JdbcBatchItemWriterBuilder<EntityOutput>()
            .dataSource(dataSource)
            .sql("INSERT INTO entity_output (id, name, value, status) " +
                 "VALUES (:id, :name, :value, :status)")
            .beanMapped()
            .build();
    }
}
```

#### 5.3 Implement File Writers
For file destinations:

1. **Create File Writer**
   - Location: `{{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}/writer/[EntityName]FileWriter.java`
   - Use FlatFileItemWriter for CSV/delimited files
   - Use StaxEventItemWriter for XML files
   - Use JsonFileItemWriter for JSON files
   - Configure field extraction

**Example Structure** (CSV File Writer):
```java
@Configuration
public class EntityFileWriterConfig {
    
    @Bean
    @StepScope
    public FlatFileItemWriter<EntityOutput> entityFileWriter(
            @Value("#{jobParameters['outputFile']}") String outputFile) {
        
        return new FlatFileItemWriterBuilder<EntityOutput>()
            .name("entityFileWriter")
            .resource(new FileSystemResource(outputFile))
            .delimited()
            .delimiter(",")
            .names(new String[]{"id", "name", "value", "status"})
            .headerCallback(writer -> writer.write("ID,Name,Value,Status"))
            .build();
    }
}
```

#### 5.4 Implement Custom Writers
For complex destinations (APIs, multiple destinations, etc.):

1. **Create Custom Writer**
   - Location: `{{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}/writer/[EntityName]CustomWriter.java`
   - Implement ItemWriter interface
   - Implement write() method
   - Handle batch writing
   - Implement error handling

**Example Structure** (API Writer):
```java
@Component
public class EntityApiWriter implements ItemWriter<EntityOutput> {
    
    private final RestTemplate restTemplate;
    private final String apiUrl;
    
    public EntityApiWriter(RestTemplate restTemplate, 
                          @Value("${api.output.url}") String apiUrl) {
        this.restTemplate = restTemplate;
        this.apiUrl = apiUrl;
    }
    
    @Override
    public void write(List<? extends EntityOutput> items) throws Exception {
        for (EntityOutput item : items) {
            try {
                restTemplate.postForObject(apiUrl, item, Void.class);
            } catch (RestClientException e) {
                throw new WriteFailedException("Failed to write item: " + item.getId(), e);
            }
        }
    }
}
```

#### 5.5 Implement Composite Writers
For writing to multiple destinations:

1. **Create Composite Writer**
   - Write to multiple destinations in one step
   - Handle partial failures appropriately

**Example Structure**:
```java
@Configuration
public class EntityCompositeWriterConfig {
    
    @Bean
    public CompositeItemWriter<EntityOutput> compositeWriter(
            ItemWriter<EntityOutput> databaseWriter,
            ItemWriter<EntityOutput> fileWriter) {
        
        CompositeItemWriter<EntityOutput> writer = new CompositeItemWriter<>();
        writer.setDelegates(Arrays.asList(databaseWriter, fileWriter));
        return writer;
    }
}
```

#### 5.6 Validate Writers
- [ ] All data destinations are written correctly
- [ ] Data format is correct
- [ ] Transaction boundaries are appropriate
- [ ] Error handling is implemented
- [ ] Writers follow batch specification patterns

### 6. Error Handling and Recovery Implementation

#### 6.1 Identify Error Handling Requirements
From the business specification, identify:
- What errors can occur (validation, processing, write failures)
- Which errors should cause job failure
- Which errors can be skipped
- Which errors should trigger retry
- What logging/reporting is needed for errors

#### 6.2 Implement Skip Logic
Configure skip policies for recoverable errors:

1. **Configure Skip Policies in Job**
   - Define which exceptions can be skipped
   - Set skip limits
   - Implement skip listeners for logging

**Example**:
```java
@Bean
public Step processStep(
        ItemReader<EntityInput> reader,
        ItemProcessor<EntityInput, EntityOutput> processor,
        ItemWriter<EntityOutput> writer) {
    return stepBuilderFactory.get("processStep")
        .<EntityInput, EntityOutput>chunk(100)
        .reader(reader)
        .processor(processor)
        .writer(writer)
        .faultTolerant()
        .skipLimit(100)
        .skip(ValidationException.class)
        .skip(DataIntegrityViolationException.class)
        .noSkip(FatalException.class)
        .listener(skipListener())
        .build();
}

@Bean
public SkipListener<EntityInput, EntityOutput> skipListener() {
    return new EntitySkipListener();
}
```

2. **Implement Skip Listener**
   - Location: `{{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}/error/[EntityName]SkipListener.java`
   - Log skipped items
   - Track skip statistics
   - Report skipped items

**Example Structure**:
```java
@Component
@Slf4j
public class EntitySkipListener implements SkipListener<EntityInput, EntityOutput> {
    
    private final SkipReportService skipReportService;
    
    public EntitySkipListener(SkipReportService skipReportService) {
        this.skipReportService = skipReportService;
    }
    
    @Override
    public void onSkipInRead(Throwable t) {
        log.warn("Skipped item during read: {}", t.getMessage());
        skipReportService.recordSkip("READ", null, t.getMessage());
    }
    
    @Override
    public void onSkipInProcess(EntityInput item, Throwable t) {
        log.warn("Skipped item during process: {} - {}", item.getId(), t.getMessage());
        skipReportService.recordSkip("PROCESS", item.getId(), t.getMessage());
    }
    
    @Override
    public void onSkipInWrite(EntityOutput item, Throwable t) {
        log.warn("Skipped item during write: {} - {}", item.getId(), t.getMessage());
        skipReportService.recordSkip("WRITE", item.getId(), t.getMessage());
    }
}
```

#### 6.3 Implement Retry Logic
Configure retry policies for transient errors:

1. **Configure Retry Policies in Job**
   - Define which exceptions should trigger retry
   - Set retry limits
   - Configure backoff policies if needed

**Example**:
```java
@Bean
public Step processStep(
        ItemReader<EntityInput> reader,
        ItemProcessor<EntityInput, EntityOutput> processor,
        ItemWriter<EntityOutput> writer) {
    return stepBuilderFactory.get("processStep")
        .<EntityInput, EntityOutput>chunk(100)
        .reader(reader)
        .processor(processor)
        .writer(writer)
        .faultTolerant()
        .retryLimit(3)
        .retry(TransientDataAccessException.class)
        .retry(DeadlockLoserDataAccessException.class)
        .retry(RestClientException.class)
        .noRetry(ValidationException.class)
        .listener(retryListener())
        .build();
}

@Bean
public RetryListener retryListener() {
    return new EntityRetryListener();
}
```

2. **Implement Retry Listener**
   - Location: `{{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}/error/[EntityName]RetryListener.java`
   - Log retry attempts
   - Track retry statistics

**Example Structure**:
```java
@Component
@Slf4j
public class EntityRetryListener implements RetryListener {
    
    @Override
    public <T, E extends Throwable> boolean open(RetryContext context, RetryCallback<T, E> callback) {
        return true;
    }
    
    @Override
    public <T, E extends Throwable> void close(RetryContext context, 
                                                RetryCallback<T, E> callback, 
                                                Throwable throwable) {
        if (throwable != null) {
            log.error("Retry failed after {} attempts", context.getRetryCount());
        }
    }
    
    @Override
    public <T, E extends Throwable> void onError(RetryContext context, 
                                                  RetryCallback<T, E> callback, 
                                                  Throwable throwable) {
        log.warn("Retry attempt {} failed: {}", 
                context.getRetryCount(), throwable.getMessage());
    }
}
```

#### 6.4 Implement Restart/Recovery Capability
Enable job restart after failure:

1. **Configure Job for Restart**
   - Use JobRepository to track execution state
   - Configure step to be restartable
   - Implement ExecutionContext for state management

**Example**:
```java
@Bean
public Job entityProcessingJob(Step processStep) {
    return jobBuilderFactory.get("entityProcessingJob")
        .incrementer(new RunIdIncrementer())
        .start(processStep)
        .listener(jobRestartListener())
        .build();
}

@Bean
public JobExecutionListener jobRestartListener() {
    return new JobExecutionListener() {
        @Override
        public void beforeJob(JobExecution jobExecution) {
            if (jobExecution.getStatus() == BatchStatus.STARTED) {
                log.info("Job restarted from previous failure");
            }
        }
        
        @Override
        public void afterJob(JobExecution jobExecution) {
            if (jobExecution.getStatus() == BatchStatus.COMPLETED) {
                log.info("Job completed successfully");
            } else if (jobExecution.getStatus() == BatchStatus.FAILED) {
                log.error("Job failed - can be restarted");
            }
        }
    };
}
```

2. **Implement Stateful Readers/Writers**
   - Save position in ExecutionContext
   - Resume from saved position on restart

**Example** (Stateful Reader):
```java
public class StatefulEntityReader implements ItemReader<EntityInput>, ItemStream {
    
    private int currentPosition = 0;
    private static final String CURRENT_POSITION_KEY = "current.position";
    
    @Override
    public void open(ExecutionContext executionContext) {
        if (executionContext.containsKey(CURRENT_POSITION_KEY)) {
            currentPosition = executionContext.getInt(CURRENT_POSITION_KEY);
            log.info("Resuming from position: {}", currentPosition);
        }
    }
    
    @Override
    public void update(ExecutionContext executionContext) {
        executionContext.putInt(CURRENT_POSITION_KEY, currentPosition);
    }
    
    @Override
    public void close() {
        // Cleanup resources
    }
    
    @Override
    public EntityInput read() throws Exception {
        // Read from current position
        EntityInput item = readFromPosition(currentPosition);
        if (item != null) {
            currentPosition++;
        }
        return item;
    }
    
    private EntityInput readFromPosition(int position) {
        // Implementation to read from specific position
        return null;
    }
}
```

#### 6.5 Implement Error Reporting
Create error reporting mechanism:

1. **Create Error Report Service**
   - Location: `{{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}/error/ErrorReportService.java`
   - Collect error information
   - Generate error reports
   - Store error details for analysis

**Example Structure**:
```java
@Service
public class ErrorReportService {
    
    private final ErrorRepository errorRepository;
    
    public ErrorReportService(ErrorRepository errorRepository) {
        this.errorRepository = errorRepository;
    }
    
    public void recordError(String phase, String itemId, String errorMessage, Throwable throwable) {
        ErrorRecord error = new ErrorRecord();
        error.setPhase(phase);
        error.setItemId(itemId);
        error.setErrorMessage(errorMessage);
        error.setStackTrace(getStackTrace(throwable));
        error.setTimestamp(LocalDateTime.now());
        
        errorRepository.save(error);
    }
    
    public void recordSkip(String phase, String itemId, String reason) {
        SkipRecord skip = new SkipRecord();
        skip.setPhase(phase);
        skip.setItemId(itemId);
        skip.setReason(reason);
        skip.setTimestamp(LocalDateTime.now());
        
        skipRepository.save(skip);
    }
    
    public ErrorReport generateReport(Long jobExecutionId) {
        List<ErrorRecord> errors = errorRepository.findByJobExecutionId(jobExecutionId);
        List<SkipRecord> skips = skipRepository.findByJobExecutionId(jobExecutionId);
        
        return new ErrorReport(errors, skips);
    }
    
    private String getStackTrace(Throwable throwable) {
        StringWriter sw = new StringWriter();
        throwable.printStackTrace(new PrintWriter(sw));
        return sw.toString();
    }
}
```

#### 6.6 Validate Error Handling
- [ ] Skip policies are configured correctly
- [ ] Retry policies are configured correctly
- [ ] Restart capability is implemented
- [ ] Error logging is comprehensive
- [ ] Error reports are generated
- [ ] Fatal errors cause job failure
- [ ] Recoverable errors are handled gracefully

### 7. Job Listeners and Monitoring

#### 7.1 Implement Job Execution Listeners
Monitor job lifecycle:

1. **Create Job Execution Listener**
   - Location: `{{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}/listener/[JobName]ExecutionListener.java`
   - Track job start/end times
   - Log job status
   - Send notifications if needed

**Example Structure**:
```java
@Component
@Slf4j
public class EntityProcessingJobListener implements JobExecutionListener {
    
    private final NotificationService notificationService;
    private final MetricsService metricsService;
    
    public EntityProcessingJobListener(NotificationService notificationService,
                                      MetricsService metricsService) {
        this.notificationService = notificationService;
        this.metricsService = metricsService;
    }
    
    @Override
    public void beforeJob(JobExecution jobExecution) {
        log.info("Job {} starting with parameters: {}", 
                jobExecution.getJobInstance().getJobName(),
                jobExecution.getJobParameters());
        
        metricsService.recordJobStart(jobExecution.getJobInstance().getJobName());
    }
    
    @Override
    public void afterJob(JobExecution jobExecution) {
        long duration = jobExecution.getEndTime().getTime() - 
                       jobExecution.getStartTime().getTime();
        
        log.info("Job {} finished with status {} in {} ms", 
                jobExecution.getJobInstance().getJobName(),
                jobExecution.getStatus(),
                duration);
        
        metricsService.recordJobEnd(
            jobExecution.getJobInstance().getJobName(),
            jobExecution.getStatus(),
            duration
        );
        
        if (jobExecution.getStatus() == BatchStatus.FAILED) {
            notificationService.sendFailureNotification(jobExecution);
        } else if (jobExecution.getStatus() == BatchStatus.COMPLETED) {
            notificationService.sendSuccessNotification(jobExecution);
        }
    }
}
```

#### 7.2 Implement Step Execution Listeners
Monitor step lifecycle:

1. **Create Step Execution Listener**
   - Location: `{{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}/listener/[StepName]ExecutionListener.java`
   - Track step start/end times
   - Log step statistics
   - Track read/write/skip counts

**Example Structure**:
```java
@Component
@Slf4j
public class EntityProcessingStepListener implements StepExecutionListener {
    
    @Override
    public void beforeStep(StepExecution stepExecution) {
        log.info("Step {} starting", stepExecution.getStepName());
    }
    
    @Override
    public ExitStatus afterStep(StepExecution stepExecution) {
        log.info("Step {} finished - Read: {}, Written: {}, Skipped: {}, Errors: {}",
                stepExecution.getStepName(),
                stepExecution.getReadCount(),
                stepExecution.getWriteCount(),
                stepExecution.getSkipCount(),
                stepExecution.getFilterCount());
        
        // Check if skip count exceeds threshold
        if (stepExecution.getSkipCount() > 100) {
            log.warn("High skip count detected: {}", stepExecution.getSkipCount());
            return ExitStatus.FAILED.addExitDescription("Too many skipped items");
        }
        
        return stepExecution.getExitStatus();
    }
}
```

#### 7.3 Implement Chunk Listeners
Monitor chunk processing:

1. **Create Chunk Listener**
   - Location: `{{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}/listener/[EntityName]ChunkListener.java`
   - Track chunk processing
   - Log progress
   - Monitor performance

**Example Structure**:
```java
@Component
@Slf4j
public class EntityChunkListener implements ChunkListener {
    
    private int chunkCount = 0;
    
    @Override
    public void beforeChunk(ChunkContext context) {
        chunkCount++;
        if (chunkCount % 10 == 0) {
            log.info("Processing chunk {}", chunkCount);
        }
    }
    
    @Override
    public void afterChunk(ChunkContext context) {
        // Chunk completed successfully
    }
    
    @Override
    public void afterChunkError(ChunkContext context) {
        log.error("Error in chunk {}", chunkCount);
    }
}
```

#### 7.4 Validate Listeners
- [ ] Job listeners are implemented
- [ ] Step listeners are implemented
- [ ] Appropriate logging is in place
- [ ] Metrics are collected
- [ ] Notifications are sent for failures
- [ ] Listeners follow batch specification patterns

### 8. Scheduling Configuration

#### 8.1 Identify Scheduling Requirements
From the business specification, identify:
- When jobs should run (daily, hourly, on-demand)
- What triggers should start jobs
- What dependencies exist between jobs
- What time windows are acceptable

#### 8.2 Implement Scheduling
Configure job scheduling based on batch specification:

**Example with Spring @Scheduled**:
```java
@Component
@Slf4j
public class EntityProcessingScheduler {
    
    private final JobLauncher jobLauncher;
    private final Job entityProcessingJob;
    
    public EntityProcessingScheduler(JobLauncher jobLauncher, Job entityProcessingJob) {
        this.jobLauncher = jobLauncher;
        this.entityProcessingJob = entityProcessingJob;
    }
    
    @Scheduled(cron = "0 0 2 * * ?") // Run daily at 2 AM
    public void runDailyProcessing() {
        try {
            JobParameters params = new JobParametersBuilder()
                .addString("processingDate", LocalDate.now().toString())
                .addLong("timestamp", System.currentTimeMillis())
                .toJobParameters();
            
            JobExecution execution = jobLauncher.run(entityProcessingJob, params);
            log.info("Job launched with execution id: {}", execution.getId());
        } catch (Exception e) {
            log.error("Failed to launch job", e);
        }
    }
}
```

**Example with Quartz**:
```java
@Configuration
public class QuartzSchedulerConfig {
    
    @Bean
    public JobDetail entityProcessingJobDetail() {
        return JobBuilder.newJob(EntityProcessingQuartzJob.class)
            .withIdentity("entityProcessingJob")
            .storeDurably()
            .build();
    }
    
    @Bean
    public Trigger entityProcessingTrigger() {
        return TriggerBuilder.newTrigger()
            .forJob(entityProcessingJobDetail())
            .withIdentity("entityProcessingTrigger")
            .withSchedule(CronScheduleBuilder.cronSchedule("0 0 2 * * ?"))
            .build();
    }
}

public class EntityProcessingQuartzJob implements Job {
    
    @Autowired
    private JobLauncher jobLauncher;
    
    @Autowired
    private Job entityProcessingJob;
    
    @Override
    public void execute(JobExecutionContext context) throws JobExecutionException {
        try {
            JobParameters params = new JobParametersBuilder()
                .addString("processingDate", LocalDate.now().toString())
                .addLong("timestamp", System.currentTimeMillis())
                .toJobParameters();
            
            jobLauncher.run(entityProcessingJob, params);
        } catch (Exception e) {
            throw new JobExecutionException("Failed to execute batch job", e);
        }
    }
}
```

#### 8.3 Validate Scheduling
- [ ] Scheduling is configured correctly
- [ ] Jobs run at specified times
- [ ] Job parameters are passed correctly
- [ ] Scheduling follows batch specification patterns

### 9. Code Quality and Best Practices

#### 9.1 Code Organization
- [ ] Code is organized by component type (config, reader, processor, writer, error, listener)
- [ ] Package structure follows batch specification
- [ ] No circular dependencies
- [ ] Proper separation of concerns

#### 9.2 Naming Conventions
- [ ] Job names follow batch specification conventions
- [ ] Step names are descriptive
- [ ] Bean names are consistent
- [ ] Class names follow conventions
- [ ] Method names are meaningful

#### 9.3 Transaction Management
- [ ] Transaction boundaries are appropriate
- [ ] Chunk size is optimized for performance
- [ ] Commit intervals are configured correctly
- [ ] Transaction propagation is correct

#### 9.4 Performance Optimization
- [ ] Chunk size is tuned for data volume
- [ ] Database queries are optimized
- [ ] Unnecessary data loading is avoided
- [ ] Parallel processing is used where appropriate

#### 9.5 Documentation
- [ ] Classes have JavaDoc comments
- [ ] Complex logic has comments
- [ ] Business rules are documented with rule IDs
- [ ] Job configuration is documented

#### 9.6 Code Style
- [ ] Code follows batch specification style guide
- [ ] Consistent indentation and formatting
- [ ] No unused imports
- [ ] No commented-out code

### 10. Compilation and Verification

#### 10.1 Compile Code
1. Navigate to batch project root
2. Run build command:
   - Maven: `mvn clean compile`
   - Gradle: `gradle clean build`
3. Verify no compilation errors

#### 10.2 Verify Implementation
- [ ] All job configurations compile
- [ ] All readers compile
- [ ] All processors compile
- [ ] All writers compile
- [ ] All listeners compile
- [ ] No compilation errors
- [ ] No warnings (or acceptable warnings only)

#### 10.3 Verify Business Rules
- [ ] All business rules from specification are implemented
- [ ] Business rules are traceable (comments with rule IDs)
- [ ] Validation rules are enforced
- [ ] Error scenarios are handled

#### 10.4 Verify Batch Patterns
- [ ] Chunk processing is configured correctly
- [ ] Transaction boundaries are appropriate
- [ ] Error handling is comprehensive
- [ ] Restart capability is implemented
- [ ] Listeners are configured

### 11. Update Progress Tracking

#### 11.1 Read Current Progress
1. Read `{{CODE_GENERATION_STATUS}}`
2. Find workpackage entry for WP-{ID}
3. If workpackage doesn't exist, create new entry

#### 11.2 Update Batch Status
Update the workpackage entry:
```json
{
  "workpackageId": "WP-{ID}",
  "workpackageName": "[Name]",
  "status": "completed",
  "tiersNeeded": ["backend", "batch"],
  "tiersCompleted": ["backend", "batch"],
  "backend": {
    "status": "completed",
    "outputLocation": "{{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}",
    "completedDate": "2026-02-16T14:30:00Z"
  },
  "frontend": null,
  "batch": {
    "status": "completed",
    "outputLocation": "{{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}",
    "completedDate": "[ISO 8601 timestamp]",
    "components": {
      "jobs": [count],
      "readers": [count],
      "processors": [count],
      "writers": [count]
    }
  },
  "completedDate": "[ISO 8601 timestamp]"
}
```

#### 11.3 Save Progress
1. Write updated progress to `{{CODE_GENERATION_STATUS}}`
2. Update lastUpdated timestamp
3. Verify file is valid JSON

### 12. Error Handling and Recovery

#### 12.1 Common Error Scenarios

1. **Missing Business Specification**
   - Detection: Business specification file not found
   - Recovery: Cannot proceed without specification
   - Escalation: Escalate to supervisor - critical blocker

2. **Ambiguous Business Rules**
   - Detection: Business rule is unclear or contradictory
   - Recovery: Document ambiguity in {{CODE_GENERATION_ERRORS}}
   - Escalation: Request clarification from supervisor

3. **Compilation Errors**
   - Detection: Code doesn't compile
   - Recovery: Fix syntax errors, missing imports, type mismatches
   - Escalation: If errors persist after fixes, escalate

4. **Missing Dependencies**
   - Detection: Required classes/libraries not available
   - Recovery: Check if Phase 4.0 completed successfully
   - Escalation: If project structure is incomplete, escalate

5. **Performance Issues**
   - Detection: Job runs too slowly or times out
   - Recovery: Tune chunk size, optimize queries, add indexes
   - Escalation: If performance requirements cannot be met, escalate

#### 12.2 Error Reporting
Document all errors in `{{CODE_GENERATION_ERRORS}}`:
```json
{
  "phase": "4.3",
  "workpackageId": "WP-{ID}",
  "timestamp": "[ISO 8601]",
  "errorType": "[Error category]",
  "description": "[What went wrong]",
  "businessRule": "[Related business rule ID if applicable]",
  "impact": "[How this affects implementation]",
  "recoveryAction": "[What was done]",
  "status": "open|resolved",
  "requiresEscalation": true|false
}
```

### 13. Completion and Handoff

#### 13.1 Completion Checklist
Before marking Phase 4.3 complete for this workpackage:
- [ ] All batch jobs configured
- [ ] All readers implemented
- [ ] All processors implemented with business logic
- [ ] All writers implemented
- [ ] All error handling implemented
- [ ] Restart/recovery capability implemented
- [ ] Code compiles without errors
- [ ] All business rules implemented and traceable
- [ ] Progress tracking updated
- [ ] No critical errors or all errors resolved

#### 13.2 Handoff to Next Workpackage
Provide to supervisor:
- Confirmation that batch tier is complete for WP-{ID}
- Location of generated code
- Component counts (jobs, readers, processors, writers)
- Any warnings or notes for next workpackage
- Confirmation that progress tracking is updated

---

## Output Format

### Batch Code Structure
**Location**: `{{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}/`

**Directory Structure**:
```
wp-{ID}/
├── config/
│   ├── EntityProcessingJobConfig.java
│   └── BatchConfiguration.java
├── reader/
│   ├── EntityRepositoryReader.java
│   ├── EntityFileReader.java
│   └── EntityCustomReader.java
├── processor/
│   ├── EntityProcessor.java
│   ├── ValidationProcessor.java
│   └── TransformationProcessor.java
├── writer/
│   ├── EntityRepositoryWriter.java
│   ├── EntityFileWriter.java
│   └── EntityCustomWriter.java
├── error/
│   ├── EntitySkipListener.java
│   ├── EntityRetryListener.java
│   └── ErrorReportService.java
└── listener/
    ├── EntityProcessingJobListener.java
    ├── EntityProcessingStepListener.java
    └── EntityChunkListener.java
```

### Progress Tracking Update
**File**: `{{CODE_GENERATION_STATUS}}`

**Updated Entry**:
```json
{
  "workpackageId": "WP-{ID}",
  "workpackageName": "[Name]",
  "status": "completed",
  "tiersNeeded": ["backend", "batch"],
  "tiersCompleted": ["backend", "batch"],
  "backend": {
    "status": "completed",
    "outputLocation": "{{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}",
    "completedDate": "2026-02-16T14:30:00Z"
  },
  "frontend": null,
  "batch": {
    "status": "completed",
    "outputLocation": "{{CODE_GENERATION_BATCH_OUTPUT}}/wp-{ID}",
    "completedDate": "2026-02-16T18:15:00Z",
    "components": {
      "jobs": 2,
      "readers": 3,
      "processors": 4,
      "writers": 2
    }
  },
  "completedDate": "2026-02-16T18:15:00Z"
}
```

---

## Quality Criteria

### Business Rule Implementation
- All business rules from business specification are implemented
- Business rules are enforced in processors
- Business rules are traceable (comments with rule IDs)
- Validation rules are applied correctly
- Error scenarios are handled per business rules

### Code Compilation
- Code compiles without errors
- No missing dependencies
- No type mismatches
- No syntax errors

### Batch Architecture
- Job configuration follows batch specification
- Chunk processing is configured correctly
- Transaction boundaries are appropriate
- Readers/processors/writers are properly separated
- No architectural violations

### Error Handling and Recovery
- Skip policies are configured correctly
- Retry policies are configured correctly
- Restart capability is implemented
- Error logging is comprehensive
- Error reports are generated
- Fatal errors cause job failure
- Recoverable errors are handled gracefully

### Performance
- Chunk size is optimized
- Database queries are efficient
- Resource usage is reasonable
- Jobs complete within acceptable timeframes

### Code Quality
- Code follows batch specification conventions
- Naming conventions followed
- Code is well-documented
- No code smells
- Proper exception handling

### Traceability
- All jobs traceable to business specification
- All business rules traceable to business specification
- All data flows traceable to business specification
- Clear mapping between requirements and implementation

---

## End of Phase 4.3 Document
