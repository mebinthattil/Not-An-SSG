import os
import json

def setup_cli():
    """
    A simple CLI to configure the static site generator.
    """
    print("--- Static Site Generator Setup ---")
    config = {}

    # --- Storage Bucket Configuration ---
    use_storage_bucket = input("Do you want to configure a storage bucket (Currently only S3 compatable buckets like CF-R2 work) [y/n]: ").lower().strip()

    if use_storage_bucket == 'y':
        print("\nPlease provide your storage bucket details. Info is stored in .env file locally.")
        bucket_name = input("Bucket Name: ")
        account_id = input("Account ID: ")
        access_key_id = input("Access Key ID: ")
        secret_access_key = input("Secret Access Key: ")
        region_name = input("Region Name: ")
        endpoint_url = input("Endpoint URL: ")
        cdn_url = input("CDN URL (eg. https://mebin.shop): ")

        with open('.env', 'w') as f:
            f.write(f"STORAGE_BUCKET_NAME={bucket_name}\n")
            f.write(f"STORAGE_ACCOUNT_ID={account_id}\n")
            f.write(f"STORAGE_ACCESS_KEY_ID={access_key_id}\n")
            f.write(f"STORAGE_SECRET_ACCESS_KEY={secret_access_key}\n")
            f.write(f"STORAGE_ENDPOINT_URL={endpoint_url}\n")
            f.write(f"STORAGE_REGION_NAME={region_name}\n")
            f.write(f"CDN_URL={cdn_url}\n")
        print("\nStorage bucket configuration saved to .env file. 👍🏻")

    else:
        print("\nSkipping storage bucket configuration.")
        if os.path.exists('.env'):
            print("An existing .env file was found. It was not modified.")



    # --- Image Dimensions Configuration ---
    print("\n--- Default Image Dimensions ---")
    set_img_dimensions = input("Do you want to set custom height and width for images in your site? [y/n]: ").lower().strip()

    if set_img_dimensions == 'y':
        print("\nPlease provide the default width and height for images in your articles.")
        default_width = input("Default image width (e.g., 800): ")
        default_height = input("Default image height (e.g., 600): ")
        
    elif set_img_dimensions == 'n':
        print("\nSkipping image dimensions configuration.")
        default_height = "500"
        default_width = "800"

    else:
        print("\nInvalid input. Please enter 'y' or 'n'.")
        return  
    
    if default_height.isdigit() and default_width.isdigit():
            config['image_dimensions'] = {
                'width': int(default_width),
                'height': int(default_height)}
    else:
        print("\nInvalid input. Please enter numeric values for width and height.")
        print("Image dimensions were not saved.")
        return



    # --- Save Configuration to JSON ---
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

    print("\n--- Setup Complete! ---")
    print("General settings saved to config.json.")
    print("You can re-run this script anytime to change your settings.")

if __name__ == "__main__":
    setup_cli()
