"""
Attribute Manager
Handles operations on PingOne custom attributes
"""


class AttributeManager:
    """Manages PingOne custom attribute operations."""
    
    def __init__(self, client, attributes, dry_run=False):
        """
        Initialize AttributeManager.
        
        Args:
            client: PingOneClient instance
            attributes: Dictionary of attributes {name: description}
            dry_run: If True, simulate operations without making changes
        """
        self.client = client
        self.attributes = attributes
        self.dry_run = dry_run
    
    def create_attributes(self):
        """
        Create custom attributes in PingOne.
        Skips attributes that already exist and displays notice.
        """
        if not self.attributes:
            print("No attributes to create.")
            return
        
        print(f"\n{'=' * 70}")
        print(f"{'ATTRIBUTE CREATION' if not self.dry_run else 'ATTRIBUTE CREATION (DRY RUN)'}")
        print(f"{'=' * 70}\n")
        
        # Header
        print(f"{'NAME':<25} {'STATUS':<15} {'RESULT':<30}")
        print(f"{'-'*25} {'-'*15} {'-'*30}")
        
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        for attr_name, description in self.attributes.items():
            try:
                # Check if attribute already exists
                success, existing_attr, error = self.client.get_attribute_by_name(attr_name)
                
                if not success:
                    print(f"{attr_name:<25} {'ERROR':<15} {'Check failed':<30}")
                    error_count += 1
                    continue
                
                if existing_attr:
                    attr_id = existing_attr.get('id', 'N/A')[:8]
                    print(f"{attr_name:<25} {'SKIPPED':<15} {f'Already exists ({attr_id}...)':<30}")
                    skipped_count += 1
                    continue
                
                # Create the attribute
                if self.dry_run:
                    print(f"{attr_name:<25} {'DRY RUN':<15} {'Would create':<30}")
                    created_count += 1
                else:
                    success, created_attr, error = self.client.create_attribute(
                        name=attr_name,
                        description=description
                    )
                    
                    if success:
                        attr_id = created_attr.get('id', 'N/A')[:8] if created_attr else 'N/A'
                        print(f"{attr_name:<25} {'CREATED':<15} {f'ID: {attr_id}...':<30}")
                        created_count += 1
                    else:
                        err_msg = str(error)[:28] if error else 'Unknown error'
                        print(f"{attr_name:<25} {'ERROR':<15} {err_msg:<30}")
                        error_count += 1
                        
            except Exception as e:
                err_msg = str(e)[:28]
                print(f"{attr_name:<25} {'ERROR':<15} {err_msg:<30}")
                error_count += 1
        
        # Summary
        print(f"\n{'=' * 70}")
        print("SUMMARY:")
        print(f"  Created: {created_count}")
        print(f"  Skipped: {skipped_count}")
        print(f"  Errors:  {error_count}")
        print(f"{'=' * 70}\n")
    
    def display_attributes(self, custom_only=False):
        """
        Display attributes defined in the system in columnar format.
        
        Args:
            custom_only: If True, only show custom attributes
        """
        print(f"\n{'=' * 70}")
        print("ATTRIBUTES IN PINGONE")
        print(f"{'=' * 70}\n")
        
        try:
            # Get all schema attributes
            success, data, error = self.client.get_schema_attributes()
            
            if not success:
                print(f"✗ ERROR: Failed to retrieve attributes: {error}")
                return
            
            if not data or '_embedded' not in data or 'attributes' not in data['_embedded']:
                print("No attributes found in the environment.")
                return
            
            all_attributes = data['_embedded']['attributes']
            
            # Filter to only requested attributes if specified
            if custom_only:
                filtered_attrs = [
                    attr for attr in all_attributes
                    if attr.get('name') in self.attributes
                ]
            else:
                # Show all attributes that match our list
                filtered_attrs = [
                    attr for attr in all_attributes
                    if attr.get('name') in self.attributes
                ]
            
            if not filtered_attrs:
                print(f"No matching attributes found.")
                return
            
            # Display attributes in columnar format
            # Header
            print(f"{'NAME':<25} {'TYPE':<10} {'STATUS':<10} {'DESCRIPTION':<30}")
            print(f"{'-'*25} {'-'*10} {'-'*10} {'-'*30}")
            
            # Rows
            for attr in sorted(filtered_attrs, key=lambda x: x.get('name', '')):
                name = attr.get('name', 'N/A')
                description = attr.get('description', 'No description')
                enabled = attr.get('enabled', False)
                data_type = attr.get('type', 'N/A')
                
                status = "Enabled" if enabled else "Disabled"
                
                # Truncate description if too long
                if len(description) > 28:
                    description = description[:28] + '..'
                
                print(f"{name:<25} {data_type:<10} {status:<10} {description:<30}")
            
            print(f"\nTotal attributes displayed: {len(filtered_attrs)}")
            print(f"{'=' * 70}\n")
            
        except Exception as e:
            print(f"✗ ERROR: Unexpected error retrieving attributes: {str(e)}")
    
    def remove_attributes(self):
        """
        Remove custom attributes from PingOne.
        """
        if not self.attributes:
            print("No attributes to remove.")
            return
        
        print(f"\n{'=' * 70}")
        print(f"{'ATTRIBUTE REMOVAL' if not self.dry_run else 'ATTRIBUTE REMOVAL (DRY RUN)'}")
        print(f"{'=' * 70}\n")
        
        # Header
        print(f"{'NAME':<25} {'STATUS':<15} {'RESULT':<30}")
        print(f"{'-'*25} {'-'*15} {'-'*30}")
        
        removed_count = 0
        not_found_count = 0
        error_count = 0
        
        for attr_name in self.attributes.keys():
            try:
                # Find the attribute
                success, existing_attr, error = self.client.get_attribute_by_name(attr_name)
                
                if not success:
                    print(f"{attr_name:<25} {'ERROR':<15} {'Check failed':<30}")
                    error_count += 1
                    continue
                
                if not existing_attr:
                    print(f"{attr_name:<25} {'NOT FOUND':<15} {'Does not exist':<30}")
                    not_found_count += 1
                    continue
                
                attr_id = existing_attr.get('id')[:8]
                
                # Delete the attribute
                if self.dry_run:
                    print(f"{attr_name:<25} {'DRY RUN':<15} {f'Would remove ({attr_id}...)':<30}")
                    removed_count += 1
                else:
                    success, _, error = self.client.delete_attribute(existing_attr.get('id'))
                    
                    if success:
                        print(f"{attr_name:<25} {'REMOVED':<15} {f'ID: {attr_id}...':<30}")
                        removed_count += 1
                    else:
                        err_msg = str(error)[:28] if error else 'Unknown error'
                        print(f"{attr_name:<25} {'ERROR':<15} {err_msg:<30}")
                        error_count += 1
                        
            except Exception as e:
                err_msg = str(e)[:28]
                print(f"{attr_name:<25} {'ERROR':<15} {err_msg:<30}")
                error_count += 1
        
        # Summary
        print(f"\n{'=' * 70}")
        print("SUMMARY:")
        print(f"  Removed:   {removed_count}")
        print(f"  Not Found: {not_found_count}")
        print(f"  Errors:    {error_count}")
        print(f"{'=' * 70}\n")
    
    def clear_attributes(self):
        """
        Clear values for attributes (disable them in PingOne).
        Note: PingOne doesn't have a direct 'clear values' operation,
        so we disable the attributes instead.
        """
        if not self.attributes:
            print("No attributes to clear.")
            return
        
        print(f"\n{'=' * 70}")
        print(f"{'ATTRIBUTE CLEARING' if not self.dry_run else 'ATTRIBUTE CLEARING (DRY RUN)'}")
        print(f"{'=' * 70}\n")
        
        # Header
        print(f"{'NAME':<25} {'STATUS':<15} {'RESULT':<30}")
        print(f"{'-'*25} {'-'*15} {'-'*30}")
        
        cleared_count = 0
        not_found_count = 0
        already_disabled_count = 0
        error_count = 0
        
        for attr_name in self.attributes.keys():
            try:
                # Find the attribute
                success, existing_attr, error = self.client.get_attribute_by_name(attr_name)
                
                if not success:
                    print(f"{attr_name:<25} {'ERROR':<15} {'Check failed':<30}")
                    error_count += 1
                    continue
                
                if not existing_attr:
                    print(f"{attr_name:<25} {'NOT FOUND':<15} {'Does not exist':<30}")
                    not_found_count += 1
                    continue
                
                attr_id = existing_attr.get('id')[:8]
                is_enabled = existing_attr.get('enabled', True)
                
                # Check if already disabled
                if not is_enabled:
                    print(f"{attr_name:<25} {'ALREADY':<15} {'Already disabled':<30}")
                    already_disabled_count += 1
                    continue
                
                # Disable the attribute (clears values)
                if self.dry_run:
                    print(f"{attr_name:<25} {'DRY RUN':<15} {f'Would disable ({attr_id}...)':<30}")
                    cleared_count += 1
                else:
                    success, _, error = self.client.update_attribute(existing_attr.get('id'), enabled=False)
                    
                    if success:
                        print(f"{attr_name:<25} {'CLEARED':<15} {f'Disabled ({attr_id}...)':<30}")
                        cleared_count += 1
                    else:
                        err_msg = str(error)[:28] if error else 'Unknown error'
                        print(f"{attr_name:<25} {'ERROR':<15} {err_msg:<30}")
                        error_count += 1
                        
            except Exception as e:
                err_msg = str(e)[:28]
                print(f"{attr_name:<25} {'ERROR':<15} {err_msg:<30}")
                error_count += 1
        
        # Summary
        print(f"\n{'=' * 70}")
        print("SUMMARY:")
        print(f"  Cleared:          {cleared_count}")
        print(f"  Already Disabled: {already_disabled_count}")
        print(f"  Not Found:        {not_found_count}")
        print(f"  Errors:           {error_count}")
        print(f"{'=' * 70}\n")
