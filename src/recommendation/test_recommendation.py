#!/usr/bin/env python
"""
Test script for the PC Parts Recommendation System.
This script runs the recommendation system with the default input.json
and prints detailed output for verification.
"""

import json
import os
import traceback
from recommendation_system import PCRecommendationSystem

def test_default_recommendation():
    """Test the recommendation system with the default input.json file"""
    print("Starting PC Parts Recommendation System test...")
    
    rec_system = None
    try:
        # Create recommendation system instance
        rec_system = PCRecommendationSystem()
        
        # Print budget allocation
        print("\nBudget Allocation:")
        for component, percentage in rec_system.budget_allocation.items():
            budget_inr = rec_system.user_prefs["budget"] * percentage
            budget_usd = budget_inr * rec_system.inr_to_usd
            print(f"  {component.ljust(12)}: {percentage * 100:.1f}% (₹{budget_inr:.2f} / ${budget_usd:.2f})")
        
        # Generate recommendation
        print("\nGenerating recommendation...")
        
        # Add component-by-component testing for debugging
        try:
            # Store any errors that occur
            errors = []
            components_selected = []
            
            # Start a transaction for all component selection
            rec_system.conn.autocommit = False
            
            print("Selecting CPU...")
            try:
                cpu = rec_system.select_cpu()
                print(f"Selected CPU: {cpu.get('name')} (Rank: {cpu.get('rank')})")
                components_selected.append("CPU")
            except Exception as e:
                print(f"Error selecting CPU: {str(e)}")
                errors.append(f"CPU: {str(e)}")
                rec_system.conn.rollback()
            
            print("Selecting Motherboard...")
            try:
                motherboard = rec_system.select_motherboard()
                print(f"Selected Motherboard: {motherboard.get('name')} (Rank: {motherboard.get('rank')})")
                components_selected.append("Motherboard")
            except Exception as e:
                print(f"Error selecting Motherboard: {str(e)}")
                errors.append(f"Motherboard: {str(e)}")
                rec_system.conn.rollback()
            
            print("Selecting CPU Cooler...")
            try:
                cooler = rec_system.select_cooler()
                print(f"Selected CPU Cooler: {cooler.get('name')} (Rank: {cooler.get('rank')})")
                components_selected.append("CPU Cooler")
            except Exception as e:
                print(f"Error selecting CPU Cooler: {str(e)}")
                errors.append(f"CPU Cooler: {str(e)}")
                rec_system.conn.rollback()
            
            print("Selecting GPU...")
            try:
                gpu = rec_system.select_gpu()
                print(f"Selected GPU: {gpu.get('name')} (Rank: {gpu.get('rank')})")
                components_selected.append("GPU")
            except Exception as e:
                print(f"Error selecting GPU: {str(e)}")
                errors.append(f"GPU: {str(e)}")
                rec_system.conn.rollback()
            
            print("Selecting Case...")
            try:
                case = rec_system.select_case()
                print(f"Selected Case: {case.get('name')} (Rank: {case.get('rank')})")
                components_selected.append("Case")
            except Exception as e:
                print(f"Error selecting Case: {str(e)}")
                errors.append(f"Case: {str(e)}")
                rec_system.conn.rollback()
            
            print("Selecting PSU...")
            try:
                psu = rec_system.select_psu()
                print(f"Selected PSU: {psu.get('name')} (Rank: {psu.get('rank')})")
                components_selected.append("PSU")
            except Exception as e:
                print(f"Error selecting PSU: {str(e)}")
                errors.append(f"PSU: {str(e)}")
                rec_system.conn.rollback()
            
            print("Selecting Memory...")
            try:
                memory = rec_system.select_memory()
                print(f"Selected Memory: {memory.get('name')} (Rank: {memory.get('rank')})")
                components_selected.append("Memory")
            except Exception as e:
                print(f"Error selecting Memory: {str(e)}")
                errors.append(f"Memory: {str(e)}")
                rec_system.conn.rollback()
            
            print("Selecting Storage...")
            try:
                storage = rec_system.select_storage()
                print(f"Selected Storage: {storage.get('name')} (Rank: {storage.get('rank')})")
                components_selected.append("Storage")
            except Exception as e:
                print(f"Error selecting Storage: {str(e)}")
                errors.append(f"Storage: {str(e)}")
                rec_system.conn.rollback()
            
            # Commit the transaction if all went well
            rec_system.conn.commit()
            
            if not errors:
                print("\nAll components selected successfully!")
            else:
                print("\nThe following errors occurred during component selection:")
                for error in errors:
                    print(f"- {error}")
                print("\nComponents successfully selected:")
                for component in components_selected:
                    print(f"- {component}")
        except Exception as component_error:
            print(f"Error during component selection: {component_error}")
            traceback.print_exc()
            # Roll back any uncommitted changes
            try:
                rec_system.conn.rollback()
            except:
                pass
            
        # Now try to get the full recommendation
        try:
            print("\nBuilding final recommendation...")
            recommendation = rec_system.build_recommendation()
            
            # Check if there was an error
            if "error" in recommendation:
                print(f"\nError occurred: {recommendation['error']}")
                print("\nComponents selected so far:")
                if "components_selected_so_far" in recommendation:
                    for comp_name, comp_data in recommendation["components_selected_so_far"].items():
                        print(f"  {comp_name}: {comp_data.get('name', 'N/A')}")
                return
            
            # Print recommendation details
            print("\nRecommended PC Build:")
            components = recommendation["components"]
            for comp_name, comp_data in components.items():
                print(f"\n{comp_name.upper()}:")
                print(f"  Name: {comp_data['name']}")
                print(f"  Price (USD): {comp_data['price']}")
                print(f"  Price (INR): {comp_data['price_inr']}")
                print("  Details:")
                for detail_name, detail_value in comp_data["details"].items():
                    print(f"    {detail_name}: {detail_value}")
            
            # Print total cost and budget information
            print(f"\nTotal Cost (USD): {recommendation['total_cost_usd']}")
            print(f"Total Cost (INR): {recommendation['total_cost_inr']}")
            print(f"Budget (INR): {recommendation['budget_inr']}")
            print(f"Budget (USD): {recommendation['budget_usd']}")
            
            total_cost_inr = float(recommendation["total_cost_inr"].replace('₹', ''))
            budget_inr = float(recommendation["budget_inr"].replace('₹', ''))
            
            if total_cost_inr <= budget_inr:
                print(f"Status: Within budget (₹{budget_inr - total_cost_inr:.2f} remaining)")
            else:
                print(f"Status: Over budget by ₹{total_cost_inr - budget_inr:.2f}")
            
            # Save recommendation to file
            output_file = "test_recommendation_result.json"
            with open(output_file, "w") as f:
                json.dump(recommendation, f, indent=2)
            print(f"\nDetailed recommendation saved to: {output_file}")
        except Exception as build_error:
            print(f"\nError building recommendation: {str(build_error)}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        traceback.print_exc()
    finally:
        # Always close database connections
        if rec_system:
            try:
                rec_system.close()
            except:
                pass

if __name__ == "__main__":
    test_default_recommendation() 