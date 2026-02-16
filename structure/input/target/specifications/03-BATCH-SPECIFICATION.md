
# Batch Specification for Java Legacy Migration Projects

**Version:** 1.0  
**Last Updated:** February 16, 2026  
**Scope:** Batch processing tier standards and requirements

---

## 1. Overview

### 1.1 Purpose

Establish consistent, maintainable, and cloud-native batch processing standards for applications migrating from mainframe batch environments, with emphasis on reliability, scalability, and observability.

### 1.2 Related Specifications

- `00-COMMON-SPECIFICATION.md` - Cross-cutting standards (MUST be followed)
- `01-FRONTEND-SPECIFICATION.md` - Frontend tier requirements
- `02-BACKEND-SPECIFICATION.md` - Backend tier requirements

### 1.3 Architecture Context

**Batch Processing Characteristics:**
- Long-running, scheduled jobs
- High-volume data processing
- Transaction-oriented processing
- Restart and recovery capabilities
- Parallel processing support
- Resource-intensive operations

**Migration Context:**
- Replace mainframe batch jobs (JCL, COBOL)
- Maintain business logic and processing rules
- Improve observability and monitoring
- Enable cloud-native deployment
- Support modern DevOps practices

---

## 2. Technology Stack

### 2.1 Core Framework

**Required:** Spring Batch 5.x

**Rationale:**
- Industry standard for batch processing
- Built-in transaction management
- Chunk-oriented processing
- Restart and recovery capabilities
- Parallel and partitioned execution
- Comprehensive monitoring and metrics

### 2.2 Java Version

**Required:** Java 17 LTS or Java 21 LTS  
**Prohibited:** Java 8, Java 11

### 2.3 Build Tool

**Recommended:** Maven 3.9.x

### 2.4 Database

**Job Repository:**
- **Recommended:** AWS RDS PostgreSQL 15.x
- Store job execution metadata
- Track job status and history
- Support restart and recovery

**Business Data:**
- Same as backend specification
- PostgreSQL, MySQL, or Aurora

### 2.5 Scheduling

**Recommended:** AWS EventBridge Scheduler

**Alternative:**
- Kubernetes CronJobs
- Spring Scheduler (for simple cases)
- Apache Airflow (for complex workflows)

### 2.6 File Processing

**Requirements:**
- AWS S3 for file storage
- Support CSV, fixed-width, XML, JSON formats
- Handle large files (>1GB)
- Support compression (gzip, zip)

---

## 3. Project Structure

### 3.1 Directory Structure

```
batch-service/
├── src/main/java/com/company/batch/
│   ├── config/              # Batch configuration
│   │   ├── BatchConfig.java
│   │   ├── DataSourceConfig.java
│   │   └── JobConfig.java
│   ├── job/                 # Job definitions
│   │   ├── resourceimport/
│   │   │   ├── ResourceImportJobConfig.java
│   │   │   ├── ResourceItemReader.java
│   │   │   ├── ResourceItemProcessor.java
│   │   │   └── ResourceItemWriter.java
│   │   └── resourceexport/
│   ├── listener/            # Job/Step listeners
│   ├── tasklet/             # Tasklet implementations
│   ├── partition/           # Partitioning logic
│   ├── model/               # Domain models
│   ├── repository/          # Data access
│   ├── service/             # Business logic
│   └── Application.java
├── src/main/resources/
│   ├── application.yml
│   ├── application-{env}.yml
│   └── db/migration/
└── pom.xml
```

### 3.2 Job Organization

**Requirements:**
- One job configuration class per job
- Separate reader, processor, writer classes
- Group related jobs in packages
- Use descriptive job and step names
- Document job purpose and schedule

---

## 4. Batch Job Design

### 4.1 Job Configuration

**Requirements:**
- Define jobs as Spring beans
- Configure job parameters
- Define job flow (steps, decisions, splits)
- Configure job listeners
- Set job restart policy

**Job Structure:**
```java
@Configuration
public class ResourceImportJobConfig {

    @Bean
    public Job resourceImportJob(JobRepository jobRepository, Step importStep) {
        return new JobBuilder("resourceImportJob", jobRepository)
            .start(importStep)
            .listener(jobExecutionListener())
            .build();
    }

    @Bean
    public Step importStep(JobRepository jobRepository, 
                          PlatformTransactionManager transactionManager,
                          ItemReader<Resource> reader,
                          ItemProcessor<Resource, Resource> processor,
                          ItemWriter<Resource> writer) {
        return new StepBuilder("importStep", jobRepository)
            .<Resource, Resource>chunk(100, transactionManager)
            .reader(reader)
            .processor(processor)
            .writer(writer)
            .faultTolerant()
            .skipLimit(10)
            .skip(ValidationException.class)
            .listener(stepExecutionListener())
            .build();
    }
}
```

### 4.2 Chunk-Oriented Processing

**Requirements:**
- Use chunk-oriented processing for large datasets
- Set appropriate chunk size (100-1000 records)
- Configure transaction boundaries
- Implement skip and retry logic
- Monitor chunk processing metrics

**Processing Flow:**
1. Read items in chunks
2. Process each item
3. Write chunk to database
4. Commit transaction
5. Repeat until complete

### 4.3 Tasklet Processing

**Requirements:**
- Use tasklets for non-item-oriented tasks
- Implement single-operation tasks
- Handle cleanup operations
- Support idempotent execution
- Return appropriate status

**Use Cases:**
- File operations (copy, move, delete)
- Database operations (truncate, index)
- External API calls
- Notification sending
- Cleanup tasks

---

## 5. Item Reader

### 5.1 Reader Types

**File Readers:**
- FlatFileItemReader (CSV, fixed-width)
- StaxEventItemReader (XML)
- JsonItemReader (JSON)

**Database Readers:**
- JdbcCursorItemReader (streaming)
- JdbcPagingItemReader (pagination)
- JpaPagingItemReader (JPA entities)

**Message Readers:**
- JmsItemReader (JMS queues)
- AmqpItemReader (RabbitMQ)

### 5.2 Reader Configuration

**Requirements:**
- Configure resource location
- Define line mapper or row mapper
- Set fetch size appropriately
- Handle empty files gracefully
- Support restart from failure point

**Best Practices:**
- Use cursor-based reading for large datasets
- Set appropriate fetch size (100-1000)
- Close resources properly
- Handle encoding correctly
- Validate file format

### 5.3 Custom Readers

**Requirements:**
- Implement ItemReader interface
- Maintain read position
- Support restart capability
- Handle exceptions appropriately
- Return null when complete

---

## 6. Item Processor

### 6.1 Processor Design

**Requirements:**
- Implement ItemProcessor interface
- Keep processing logic focused
- Validate input data
- Transform data as needed
- Handle business rules
- Return null to filter items

**Processing Responsibilities:**
- Data validation
- Data transformation
- Business rule application
- Enrichment from external sources
- Filtering invalid records

### 6.2 Composite Processors

**Requirements:**
- Chain multiple processors
- Use CompositeItemProcessor
- Keep individual processors simple
- Maintain single responsibility
- Support reusability

### 6.3 Error Handling

**Requirements:**
- Validate all input data
- Throw exceptions for invalid data
- Log processing errors
- Support skip logic
- Track skipped items

---

## 7. Item Writer

### 7.1 Writer Types

**File Writers:**
- FlatFileItemWriter (CSV, fixed-width)
- StaxEventItemWriter (XML)
- JsonFileItemWriter (JSON)

**Database Writers:**
- JdbcBatchItemWriter (JDBC batch)
- JpaItemWriter (JPA entities)
- RepositoryItemWriter (Spring Data)

**Message Writers:**
- JmsItemWriter (JMS queues)
- AmqpItemWriter (RabbitMQ)

### 7.2 Writer Configuration

**Requirements:**
- Configure output location
- Define field extractor or line aggregator
- Set batch size appropriately
- Handle write failures
- Support transactional writes

**Best Practices:**
- Use batch writes for performance
- Set appropriate batch size (100-1000)
- Handle duplicate keys
- Validate output format
- Close resources properly

### 7.3 Custom Writers

**Requirements:**
- Implement ItemWriter interface
- Write items in batch
- Handle partial failures
- Support transactions
- Clean up resources

---

## 8. Job Parameters

### 8.1 Parameter Definition

**Requirements:**
- Define job parameters in job configuration
- Use JobParameters for runtime values
- Support parameter validation
- Document required parameters
- Provide default values when appropriate

**Parameter Types:**
- String parameters
- Long parameters (timestamps)
- Date parameters
- Double parameters

### 8.2 Parameter Usage

**Requirements:**
- Access parameters via JobParameters
- Use parameters in readers/writers
- Include parameters in job identity
- Validate parameter values
- Log parameter values

**Common Parameters:**
- Input file path
- Output file path
- Processing date
- Batch ID
- Environment

---

## 9. Job Execution

### 9.1 Job Launcher

**Requirements:**
- Use JobLauncher to start jobs
- Pass JobParameters
- Handle job execution exceptions
- Return JobExecution
- Support synchronous and asynchronous execution

### 9.2 Job Scheduling

**Requirements:**
- Schedule jobs using EventBridge Scheduler
- Define cron expressions
- Handle timezone correctly
- Support one-time and recurring jobs
- Monitor scheduled executions

**Scheduling Patterns:**
- Daily jobs (e.g., 0 2 * * *)
- Hourly jobs (e.g., 0 * * * *)
- Weekly jobs (e.g., 0 2 * * 0)
- Monthly jobs (e.g., 0 2 1 * *)

### 9.3 Manual Execution

**Requirements:**
- Support manual job triggering
- Provide REST API for job execution
- Validate job parameters
- Return execution status
- Support job stopping

---

## 10. Restart and Recovery

### 10.1 Job Restart

**Requirements:**
- Enable job restart capability
- Store execution state in job repository
- Resume from last successful chunk
- Handle incomplete transactions
- Validate restart conditions

**Restart Scenarios:**
- Application crash
- Database connection failure
- File processing error
- Business validation failure

### 10.2 Skip Logic

**Requirements:**
- Configure skip limit
- Define skippable exceptions
- Log skipped items
- Track skip count
- Fail job if skip limit exceeded

### 10.3 Retry Logic

**Requirements:**
- Configure retry limit
- Define retryable exceptions
- Implement exponential backoff
- Log retry attempts
- Fail after max retries

---

## 11. Parallel Processing

### 11.1 Multi-Threading

**Requirements:**
- Configure thread pool size
- Use TaskExecutor for parallel steps
- Handle thread safety
- Monitor thread usage
- Set appropriate pool size (CPU cores * 2)

### 11.2 Partitioning

**Requirements:**
- Partition large datasets
- Define partition strategy
- Configure partition size
- Aggregate partition results
- Handle partition failures

**Partitioning Strategies:**
- Range partitioning (by ID range)
- Hash partitioning (by hash value)
- Column partitioning (by column value)
- File partitioning (by file)

### 11.3 Remote Chunking

**Requirements:**
- Separate reading from processing/writing
- Use message queues for communication
- Configure chunk size
- Handle worker failures
- Monitor worker status

---

## 12. File Processing

### 12.1 File Formats

**CSV Files:**
- Define delimiter
- Handle quoted fields
- Support header row
- Handle empty fields
- Validate column count

**Fixed-Width Files:**
- Define field ranges
- Handle padding
- Support alignment (left/right)
- Trim whitespace
- Validate record length

**XML Files:**
- Define root element
- Define record element
- Handle namespaces
- Validate against schema
- Support large files

**JSON Files:**
- Define record structure
- Handle nested objects
- Support arrays
- Validate against schema
- Support streaming

### 12.2 File Operations

**Requirements:**
- Read from S3
- Write to S3
- Support file compression
- Handle large files (streaming)
- Validate file existence
- Handle file encoding

### 12.3 File Validation

**Requirements:**
- Validate file format
- Validate file size
- Validate record count
- Validate checksums
- Generate validation report

---

## 13. Database Operations

### 13.1 Batch Updates

**Requirements:**
- Use JDBC batch updates
- Set appropriate batch size
- Handle batch failures
- Monitor batch performance
- Use prepared statements

### 13.2 Transaction Management

**Requirements:**
- Configure transaction manager
- Set transaction timeout
- Define transaction boundaries
- Handle transaction failures
- Support nested transactions

### 13.3 Database Performance

**Requirements:**
- Disable indexes during bulk load
- Rebuild indexes after load
- Use bulk insert operations
- Optimize query performance
- Monitor database connections

---

## 14. Error Handling

### 14.1 Exception Handling

**Requirements:**
- Define exception hierarchy
- Handle skippable exceptions
- Handle retryable exceptions
- Handle fatal exceptions
- Log all exceptions with context

**Exception Types:**
- ValidationException (skip)
- TransientException (retry)
- FatalException (fail immediately)

### 14.2 Error Reporting

**Requirements:**
- Log error details
- Track error count
- Generate error report
- Notify on critical errors
- Store error records

### 14.3 Failure Recovery

**Requirements:**
- Support job restart
- Clean up partial data
- Rollback failed transactions
- Notify stakeholders
- Document recovery steps

---

## 15. Monitoring and Logging

### 15.1 Job Monitoring

**Requirements:**
- Track job execution status
- Monitor job duration
- Track processed item count
- Monitor skip/retry counts
- Alert on job failures

**Metrics to Track:**
- Job start/end time
- Job duration
- Items read/processed/written
- Skip count
- Retry count
- Error count

### 15.2 Logging

**Requirements:**
- Log job start/end
- Log step start/end
- Log chunk processing
- Log errors with context
- Include correlation ID
- Use structured logging

**Log Levels:**
- INFO - Job/step lifecycle events
- WARN - Skipped items, retries
- ERROR - Job failures, exceptions
- DEBUG - Detailed processing info

### 15.3 Job Repository

**Requirements:**
- Store job execution metadata
- Track job parameters
- Store execution context
- Support job history queries
- Clean up old executions

---

## 16. Testing

### 16.1 Testing Strategy

**Test Types:**
- Unit Tests: 70% (readers, processors, writers)
- Integration Tests: 20% (job execution)
- End-to-End Tests: 10% (full job flow)

**Coverage Requirements:**
- Minimum 80% code coverage
- 100% coverage for business logic
- All error scenarios tested

### 16.2 Unit Testing

**Requirements:**
- Test readers in isolation
- Test processors with sample data
- Test writers with mock output
- Mock external dependencies
- Test error handling

### 16.3 Integration Testing

**Requirements:**
- Use in-memory job repository
- Use test database
- Test complete job execution
- Test restart scenarios
- Test skip/retry logic

**Test Scenarios:**
- Successful job execution
- Job restart after failure
- Skip logic with invalid data
- Retry logic with transient errors
- Parallel processing

### 16.4 Performance Testing

**Requirements:**
- Test with production-like data volumes
- Measure job duration
- Monitor resource usage
- Test parallel processing
- Identify bottlenecks

---

## 17. Performance Optimization

### 17.1 Chunk Size Tuning

**Requirements:**
- Start with chunk size 100-1000
- Measure performance
- Adjust based on metrics
- Consider memory constraints
- Balance throughput and latency

### 17.2 Database Optimization

**Requirements:**
- Use batch operations
- Optimize queries
- Use appropriate indexes
- Configure connection pool
- Monitor database performance

### 17.3 File Processing Optimization

**Requirements:**
- Use streaming for large files
- Enable compression
- Use parallel processing
- Optimize I/O operations
- Monitor file processing time

### 17.4 Memory Management

**Requirements:**
- Monitor heap usage
- Avoid loading entire file in memory
- Use streaming readers/writers
- Configure appropriate heap size
- Handle large objects carefully

---

## 18. Security

### 18.1 Authentication

**Requirements:**
- Authenticate job execution requests
- Use service accounts for scheduled jobs
- Rotate credentials regularly
- Store credentials securely
- Audit job executions

### 18.2 Authorization

**Requirements:**
- Control job execution permissions
- Restrict access to job repository
- Control file access permissions
- Audit authorization failures
- Implement role-based access

### 18.3 Data Security

**Requirements:**
- Encrypt sensitive data at rest
- Encrypt data in transit
- Mask sensitive data in logs
- Secure file storage (S3 encryption)
- Implement data retention policies

---

## 19. Deployment

### 19.1 Docker Configuration

**Requirements:**
- Use multi-stage Dockerfile
- Minimize image size
- Run as non-root user
- Include health check
- Set resource limits

### 19.2 Kubernetes Deployment

**Requirements:**
- Define Job resource for one-time jobs
- Define CronJob resource for scheduled jobs
- Configure resource requests/limits
- Set job completion/failure policies
- Configure restart policy

**Resource Limits:**
- Memory request: 1Gi
- Memory limit: 2Gi
- CPU request: 500m
- CPU limit: 1000m

### 19.3 Environment Configuration

**Requirements:**
- Use Spring profiles
- Externalize configuration
- Use environment variables
- Support multiple environments
- Validate configuration on startup

---

## 20. Migration Patterns

### 20.1 JCL to Spring Batch

**Mapping:**
- JCL JOB → Spring Batch Job
- JCL STEP → Spring Batch Step
- JCL DD → ItemReader/ItemWriter
- JCL PROC → Reusable Step/Tasklet
- JCL COND → Step Execution Decision

### 20.2 COBOL Program Migration

**Approach:**
- Extract business logic
- Identify file operations
- Map to reader/processor/writer
- Preserve business rules
- Maintain data transformations

### 20.3 Data Format Migration

**Requirements:**
- Map EBCDIC to UTF-8
- Convert fixed-width to CSV/JSON
- Handle packed decimal fields
- Preserve data precision
- Validate converted data

### 20.4 Control File Migration

**Mapping:**
- Control cards → Job parameters
- Restart logic → Spring Batch restart
- Checkpoint logic → Chunk commits
- Error handling → Skip/retry logic

---

## 21. Prohibited Practices

### 21.1 Code Anti-Patterns

**Prohibited:**
- Processing entire file in memory
- Using infinite loops
- Ignoring exceptions
- Not implementing restart logic
- Hardcoding file paths
- Not closing resources

### 21.2 Performance Anti-Patterns

**Prohibited:**
- Single-threaded processing of large datasets
- Not using batch operations
- Loading unnecessary data
- Not using indexes
- Synchronous processing when async possible
- Not monitoring performance

### 21.3 Data Anti-Patterns

**Prohibited:**
- Not validating input data
- Not handling duplicate records
- Not tracking processed records
- Not implementing idempotency
- Not archiving processed files
- Not implementing data retention

---

## 22. Best Practices

### 22.1 Job Design

**Best Practices:**
- Keep jobs focused and single-purpose
- Design for idempotency
- Implement comprehensive logging
- Support restart from any point
- Handle all error scenarios
- Document job dependencies

### 22.2 Data Processing

**Best Practices:**
- Validate data early
- Process in chunks
- Use parallel processing for large volumes
- Implement skip logic for bad records
- Track processing metrics
- Archive processed files

### 22.3 Operations

**Best Practices:**
- Monitor all job executions
- Alert on failures
- Implement retry logic
- Document operational procedures
- Maintain job execution history
- Regular cleanup of old data

---

## 23. Document Control

### 23.1 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-16 | Architecture Team | Initial version |

### 23.2 Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Technical Lead | | | |
| Architecture Lead | | | |
| Operations Lead | | | |

### 23.3 Review Schedule

This document should be reviewed and updated:
- Quarterly for minor updates
- Annually for major revisions
- When new technologies are adopted
- When processing patterns change

### 23.4 Related Documents

- Common Specification
- Frontend Specification
- Backend Specification
- Operations Guide
- Migration Playbook
- Monitoring Guide

---

**End of Batch Specification**
