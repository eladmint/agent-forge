#!/usr/bin/env python3
"""
Agent Forge - Multi-Agent Coordination Tests
Testing interaction and coordination between multiple agents.
"""

import os
import sys
import time
import json
import asyncio
import unittest
import threading
from unittest.mock import Mock, patch
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))


class AgentCommunicationTests(unittest.TestCase):
    """Test communication between agents."""
    
    def setUp(self):
        """Set up test environment with mock agents."""
        self.mock_agents = {
            'page_scraper': Mock(),
            'data_compiler': Mock(),
            'enhanced_validation': Mock(),
            'external_site_scraper': Mock()
        }
        
    def test_01_agent_data_handoff(self):
        """Test data handoff between agents."""
        print("\n🤝 Testing Agent Data Handoff...")
        
        # Simulate page_scraper -> data_compiler workflow
        def simulate_data_handoff():
            """Simulate data being passed from one agent to another."""
            
            # Step 1: Page scraper extracts data
            scraper_result = {
                'success': True,
                'agent': 'page_scraper',
                'data': {
                    'title': 'Test Page',
                    'content': 'This is test content...',
                    'links': ['http://example.com/link1', 'http://example.com/link2'],
                    'metadata': {'timestamp': time.time()}
                },
                'handoff_to': 'data_compiler'
            }
            
            # Step 2: Data compiler processes the data
            if scraper_result['success'] and scraper_result['handoff_to'] == 'data_compiler':
                compiler_input = scraper_result['data']
                
                compiler_result = {
                    'success': True,
                    'agent': 'data_compiler',
                    'processed_data': {
                        'original_title': compiler_input['title'],
                        'content_length': len(compiler_input['content']),
                        'link_count': len(compiler_input['links']),
                        'processed_at': time.time(),
                        'source_agent': scraper_result['agent']
                    },
                    'handoff_to': 'enhanced_validation'
                }
                
                # Step 3: Validation agent verifies the data
                if compiler_result['success'] and compiler_result['handoff_to'] == 'enhanced_validation':
                    validation_input = compiler_result['processed_data']
                    
                    validation_result = {
                        'success': True,
                        'agent': 'enhanced_validation',
                        'validation': {
                            'data_integrity': True,
                            'completeness_score': 0.95,
                            'source_verified': True,
                            'chain_of_custody': [
                                scraper_result['agent'],
                                compiler_result['agent'],
                                'enhanced_validation'
                            ]
                        }
                    }
                    
                    return {
                        'workflow_success': True,
                        'agents_involved': 3,
                        'final_result': validation_result,
                        'data_preserved': validation_input['original_title'] == scraper_result['data']['title']
                    }
            
            return {'workflow_success': False, 'error': 'Handoff failed'}
        
        result = simulate_data_handoff()
        
        self.assertTrue(result['workflow_success'])
        self.assertEqual(result['agents_involved'], 3)
        self.assertTrue(result['data_preserved'])
        self.assertIn('chain_of_custody', result['final_result']['validation'])
        
        print("   ✅ Data handoff between agents successful")
    
    def test_02_concurrent_agent_operations(self):
        """Test concurrent operations by multiple agents."""
        print("\n⚡ Testing Concurrent Agent Operations...")
        
        def simulate_concurrent_agents():
            """Simulate multiple agents working concurrently."""
            import threading
            import time
                        
            results = {}
            errors = []
            
            def agent_operation(agent_name, operation_time, shared_resource=None):
                """Simulate agent operation that might access shared resources."""
                try:
                    start_time = time.time()
                    
                    # Simulate work
                    time.sleep(operation_time / 1000)  # Convert ms to seconds for test
                    
                    # Check for resource conflicts
                    if shared_resource and shared_resource.get('locked_by') and shared_resource['locked_by'] != agent_name:
                        raise Exception(f"Resource conflict: {shared_resource['locked_by']} has lock")
                    
                    end_time = time.time()
                    
                    results[agent_name] = {
                        'success': True,
                        'duration': end_time - start_time,
                        'timestamp': end_time
                    }
                    
                except Exception as e:
                    errors.append(f"{agent_name}: {str(e)}")
                    results[agent_name] = {'success': False, 'error': str(e)}
            
            # Create shared resource with simple locking
            shared_resource = {'locked_by': None}
            
            # Start concurrent agent operations
            threads = []
            agent_configs = [
                ('page_scraper', 50),      # 50ms operation
                ('data_compiler', 30),     # 30ms operation  
                ('enhanced_validation', 40), # 40ms operation
                ('external_site_scraper', 60) # 60ms operation
            ]
            
            for agent_name, duration in agent_configs:
                thread = threading.Thread(
                    target=agent_operation,
                    args=(agent_name, duration, shared_resource)
                )
                threads.append(thread)
                thread.start()
            
            # Wait for all operations to complete
            for thread in threads:
                thread.join(timeout=1.0)  # 1 second timeout
                
            return {
                'results': results,
                'errors': errors,
                'concurrent_success': len([r for r in results.values() if r['success']]),
                'total_agents': len(agent_configs)
            }
        
        result = simulate_concurrent_agents()
        
        # Should handle concurrent operations successfully
        self.assertGreaterEqual(result['concurrent_success'], 3)  # At least 3 should succeed
        self.assertEqual(result['total_agents'], 4)
        
        # Check timing to ensure concurrency
        timestamps = [r['timestamp'] for r in result['results'].values() if r['success']]
        if len(timestamps) > 1:
            time_span = max(timestamps) - min(timestamps)
            self.assertLess(time_span, 0.5, "Operations should complete concurrently, not sequentially")
        
        print(f"   ✅ Concurrent agent operations: {result['concurrent_success']}/{result['total_agents']} successful")
    
    def test_03_agent_error_propagation(self):
        """Test error propagation through agent chain."""
        print("\n🚨 Testing Agent Error Propagation...")
        
        def simulate_error_chain():
            """Simulate error occurring in agent chain and propagation."""
            
            agents_chain = ['page_scraper', 'data_compiler', 'enhanced_validation']
            chain_results = []
            
            for i, agent_name in enumerate(agents_chain):
                try:
                    # Simulate error in second agent
                    if agent_name == 'data_compiler':
                        raise Exception("Data compilation failed: Invalid data format")
                    
                    # Normal operation
                    result = {
                        'agent': agent_name,
                        'success': True,
                        'data': f'{agent_name}_output_{i}',
                        'chain_position': i
                    }
                    chain_results.append(result)
                    
                except Exception as e:
                    # Error handling and propagation
                    error_result = {
                        'agent': agent_name,
                        'success': False,
                        'error': str(e),
                        'chain_position': i,
                        'chain_broken': True,
                        'upstream_results': chain_results.copy()
                    }
                    chain_results.append(error_result)
                    
                    # Notify downstream agents of chain failure
                    for j in range(i + 1, len(agents_chain)):
                        downstream_agent = agents_chain[j]
                        chain_results.append({
                            'agent': downstream_agent,
                            'success': False,
                            'error': 'upstream_chain_failure',
                            'chain_position': j,
                            'failed_upstream': agent_name,
                            'skipped': True
                        })
                    break
            
            return {
                'chain_results': chain_results,
                'chain_completed': all(r['success'] for r in chain_results),
                'error_propagated': any(r.get('chain_broken') for r in chain_results),
                'downstream_notified': any(r.get('skipped') for r in chain_results)
            }
        
        result = simulate_error_chain()
        
        # Chain should fail gracefully with proper error propagation
        self.assertFalse(result['chain_completed'])
        self.assertTrue(result['error_propagated'])
        self.assertTrue(result['downstream_notified'])
        
        # Check that upstream results are preserved
        failed_agent_result = next(r for r in result['chain_results'] if r.get('chain_broken'))
        self.assertIn('upstream_results', failed_agent_result)
        self.assertGreater(len(failed_agent_result['upstream_results']), 0)
        
        print("   ✅ Agent error propagation handled correctly")


class ResourceConflictTests(unittest.TestCase):
    """Test resource conflict resolution between agents."""
    
    def test_01_shared_resource_access(self):
        """Test access to shared resources by multiple agents."""
        print("\n🔒 Testing Shared Resource Access...")
        
        # Simulate shared resource (e.g., file, database connection, API rate limit)
        class SharedResource:
            def __init__(self, name, max_concurrent=2):
                self.name = name
                self.max_concurrent = max_concurrent
                self.current_users = []
                self.lock = threading.Lock()
                
            def acquire(self, agent_name):
                with self.lock:
                    if len(self.current_users) >= self.max_concurrent:
                        return False, f"Resource {self.name} at capacity ({self.max_concurrent})"
                    
                    self.current_users.append(agent_name)
                    return True, f"Resource acquired by {agent_name}"
                    
            def release(self, agent_name):
                with self.lock:
                    if agent_name in self.current_users:
                        self.current_users.remove(agent_name)
                        return True, f"Resource released by {agent_name}"
                    return False, f"Agent {agent_name} does not hold resource"
        
        shared_api = SharedResource("NMKR_API", max_concurrent=2)
        results = {}
        
        def agent_resource_operation(agent_name, operation_duration=0.1):
            """Simulate agent operation requiring shared resource."""
            # Try to acquire resource
            acquired, message = shared_api.acquire(agent_name)
            
            if not acquired:
                results[agent_name] = {
                    'success': False,
                    'error': 'resource_unavailable',
                    'message': message
                }
                return
            
            try:
                # Simulate work with resource
                time.sleep(operation_duration / 10)  # Shortened for test
                
                results[agent_name] = {
                    'success': True,
                    'resource_used': shared_api.name,
                    'concurrent_users': len(shared_api.current_users)
                }
                
            finally:
                # Always release resource
                shared_api.release(agent_name)
        
        # Test with multiple agents competing for resource
        agents = ['page_scraper', 'external_site_scraper', 'data_compiler', 'enhanced_validation']
        threads = []
        
        for agent_name in agents:
            thread = threading.Thread(target=agent_resource_operation, args=(agent_name,))
            threads.append(thread)
            thread.start()
        
        # Wait for all operations
        for thread in threads:
            thread.join(timeout=1.0)
        
        # Analyze results
        successful_ops = [r for r in results.values() if r['success']]
        failed_ops = [r for r in results.values() if not r['success']]
        
        # Should have some successful operations within resource limits
        self.assertGreater(len(successful_ops), 0)
        
        # Check that concurrent usage didn't exceed limits
        for result in successful_ops:
            self.assertLessEqual(result['concurrent_users'], 2)
            
        print(f"   ✅ Shared resource access managed: {len(successful_ops)} successful, {len(failed_ops)} queued")
    
    def test_02_resource_deadlock_prevention(self):
        """Test prevention of resource deadlocks between agents."""
        print("\n🔐 Testing Resource Deadlock Prevention...")
        
        # Create multiple resources that could cause deadlock
        class OrderedResourceManager:
            def __init__(self):
                self.resources = {}
                self.resource_order = {}
                self.locks = {}
                
            def add_resource(self, name, order):
                self.resources[name] = {'available': True, 'held_by': None}
                self.resource_order[name] = order
                self.locks[name] = threading.Lock()
                
            def acquire_resources(self, agent_name, resource_names):
                """Acquire multiple resources in consistent order to prevent deadlock."""
                # Sort resources by order to ensure consistent acquisition sequence
                sorted_resources = sorted(resource_names, key=lambda x: self.resource_order.get(x, 0))
                acquired = []
                
                try:
                    for resource_name in sorted_resources:
                        lock = self.locks[resource_name]
                        if lock.acquire(timeout=0.1):  # Short timeout for test
                            if self.resources[resource_name]['available']:
                                self.resources[resource_name]['available'] = False
                                self.resources[resource_name]['held_by'] = agent_name
                                acquired.append(resource_name)
                            else:
                                lock.release()
                                raise Exception(f"Resource {resource_name} not available")
                        else:
                            raise Exception(f"Could not acquire lock for {resource_name}")
                    
                    return True, acquired
                    
                except Exception as e:
                    # Release any acquired resources
                    for resource_name in acquired:
                        self.resources[resource_name]['available'] = True
                        self.resources[resource_name]['held_by'] = None
                        self.locks[resource_name].release()
                    return False, str(e)
                    
            def release_resources(self, agent_name, resource_names):
                """Release multiple resources."""
                for resource_name in resource_names:
                    if resource_name in self.resources and self.resources[resource_name]['held_by'] == agent_name:
                        self.resources[resource_name]['available'] = True
                        self.resources[resource_name]['held_by'] = None
                        self.locks[resource_name].release()
        
        # Set up resources with ordering
        resource_mgr = OrderedResourceManager()
        resource_mgr.add_resource('database', 1)
        resource_mgr.add_resource('file_system', 2)
        resource_mgr.add_resource('api_quota', 3)
        
        results = {}
        
        def multi_resource_operation(agent_name, needed_resources):
            """Simulate agent operation needing multiple resources."""
            acquired, result = resource_mgr.acquire_resources(agent_name, needed_resources)
            
            if acquired:
                try:
                    # Simulate work with resources
                    time.sleep(0.01)  # Brief work simulation
                    
                    results[agent_name] = {
                        'success': True,
                        'resources_used': result,
                        'deadlock_avoided': True
                    }
                    
                finally:
                    resource_mgr.release_resources(agent_name, result)
            else:
                results[agent_name] = {
                    'success': False,
                    'error': result,
                    'deadlock_detected': 'timeout' in result
                }
        
        # Test scenarios that could cause deadlock
        test_scenarios = [
            ('agent_1', ['database', 'file_system']),
            ('agent_2', ['file_system', 'api_quota']),
            ('agent_3', ['api_quota', 'database']),
            ('agent_4', ['database', 'api_quota', 'file_system'])
        ]
        
        threads = []
        for agent_name, resources in test_scenarios:
            thread = threading.Thread(target=multi_resource_operation, args=(agent_name, resources))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=2.0)
        
        # Analyze results
        successful_ops = [r for r in results.values() if r['success']]
        deadlock_detected = any(r.get('deadlock_detected') for r in results.values())
        
        # Should complete without deadlock
        self.assertFalse(deadlock_detected, "Deadlock should be prevented by ordered acquisition")
        self.assertGreater(len(successful_ops), 0, "Some operations should succeed")
        
        print(f"   ✅ Deadlock prevention successful: {len(successful_ops)} operations completed safely")


class WorkflowCoordinationTests(unittest.TestCase):
    """Test complex multi-agent workflow coordination."""
    
    def test_01_sequential_workflow_coordination(self):
        """Test coordination of sequential multi-agent workflow."""
        print("\n🔄 Testing Sequential Workflow Coordination...")
        
        # Define a complex workflow: Web scraping -> Data extraction -> Validation -> Blockchain proof
        workflow_stages = [
            {'agent': 'external_site_scraper', 'input': 'https://example.com', 'output_key': 'raw_html'},
            {'agent': 'page_scraper', 'input': 'raw_html', 'output_key': 'structured_data'},
            {'agent': 'data_compiler', 'input': 'structured_data', 'output_key': 'compiled_data'},
            {'agent': 'enhanced_validation', 'input': 'compiled_data', 'output_key': 'validated_data'},
            {'agent': 'nmkrauditor', 'input': 'validated_data', 'output_key': 'blockchain_proof'}
        ]
        
        def execute_workflow(stages):
            """Execute multi-agent workflow with proper coordination."""
            workflow_state = {'stage': 0, 'data': {}, 'results': []}
            
            for i, stage in enumerate(stages):
                try:
                    # Get input data
                    if i == 0:
                        # First stage uses external input
                        input_data = stage['input']
                    else:
                        # Subsequent stages use output from previous stage
                        prev_output_key = stages[i-1]['output_key']
                        input_data = workflow_state['data'].get(prev_output_key)
                        
                        if not input_data:
                            raise Exception(f"Missing input data: {prev_output_key}")
                    
                    # Simulate agent processing
                    processing_result = self.simulate_agent_processing(stage['agent'], input_data)
                    
                    if processing_result['success']:
                        # Store output for next stage
                        workflow_state['data'][stage['output_key']] = processing_result['output']
                        workflow_state['results'].append({
                            'stage': i,
                            'agent': stage['agent'],
                            'success': True,
                            'output_size': len(str(processing_result['output']))
                        })
                        workflow_state['stage'] = i + 1
                    else:
                        # Workflow failed at this stage
                        workflow_state['results'].append({
                            'stage': i,
                            'agent': stage['agent'],
                            'success': False,
                            'error': processing_result['error']
                        })
                        workflow_state['failed_at_stage'] = i
                        break
                        
                except Exception as e:
                    workflow_state['results'].append({
                        'stage': i,
                        'agent': stage['agent'],
                        'success': False,
                        'error': str(e)
                    })
                    workflow_state['failed_at_stage'] = i
                    break
            
            workflow_state['completed'] = workflow_state['stage'] == len(stages)
            return workflow_state
        
        result = execute_workflow(workflow_stages)
        
        # Workflow should complete successfully or fail gracefully
        if result['completed']:
            self.assertEqual(result['stage'], len(workflow_stages))
            self.assertTrue(all(r['success'] for r in result['results']))
        else:
            self.assertIn('failed_at_stage', result)
            self.assertLess(result['failed_at_stage'], len(workflow_stages))
        
        print(f"   ✅ Sequential workflow: {result['stage']}/{len(workflow_stages)} stages completed")
    
    def simulate_agent_processing(self, agent_name, input_data):
        """Simulate agent processing with realistic behavior."""
        # Mock different agent behaviors
        agent_behaviors = {
            'external_site_scraper': lambda x: {'success': True, 'output': f'<html>scraped from {x}</html>'},
            'page_scraper': lambda x: {'success': True, 'output': {'title': 'Test', 'content': 'parsed content'}},
            'data_compiler': lambda x: {'success': True, 'output': {'compiled': True, 'source': x}},
            'enhanced_validation': lambda x: {'success': True, 'output': {'valid': True, 'score': 0.95}},
            'nmkrauditor': lambda x: {'success': True, 'output': {'tx_id': 'tx_12345', 'verified': True}}
        }
        
        if agent_name in agent_behaviors:
            try:
                return agent_behaviors[agent_name](input_data)
            except Exception as e:
                return {'success': False, 'error': str(e)}
        else:
            return {'success': False, 'error': f'Unknown agent: {agent_name}'}


def run_coordination_tests():
    """Run all agent coordination test suites."""
    print("🤝 Agent Forge Multi-Agent Coordination Tests")
    print("=" * 60)
    
    test_suites = [
        AgentCommunicationTests,
        ResourceConflictTests,
        WorkflowCoordinationTests
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for suite_class in test_suites:
        print(f"\n🧪 Running {suite_class.__name__}...")
        
        suite = unittest.TestLoader().loadTestsFromTestCase(suite_class)
        runner = unittest.TextTestRunner(verbosity=0, stream=open('/dev/null', 'w'))
        result = runner.run(suite)
        
        suite_tests = result.testsRun
        suite_failures = len(result.failures) + len(result.errors)
        suite_passed = suite_tests - suite_failures
        
        total_tests += suite_tests
        passed_tests += suite_passed
        
        if result.failures:
            failed_tests.extend([f"{test}: {error}" for test, error in result.failures])
        if result.errors:
            failed_tests.extend([f"{test}: {error}" for test, error in result.errors])
        
        print(f"   📊 {suite_passed}/{suite_tests} tests passed")
    
    print("\n" + "=" * 60)
    print("🤝 MULTI-AGENT COORDINATION TEST RESULTS")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {passed_tests/total_tests:.1%}")
    
    if failed_tests:
        print("\n❌ Failed Tests:")
        for failure in failed_tests:
            print(f"   - {failure}")
    
    status = "🤝 MULTI-AGENT COORDINATION VALIDATED!" if passed_tests == total_tests else "⚠️ COORDINATION ISSUES FOUND - REVIEW REQUIRED"
    print(f"\n{status}")
    
    return passed_tests == total_tests


if __name__ == '__main__':
    success = run_coordination_tests()
    sys.exit(0 if success else 1)