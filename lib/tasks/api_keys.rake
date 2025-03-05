namespace :api_keys do
  desc "Generate a new API key"
  task :generate, [:name] => :environment do |t, args|
    if args[:name].blank?
      puts "Please provide a name for the API key"
      puts "Usage: rake api_keys:generate['Key Name']"
      exit 1
    end

    api_key = ApiKey.create!(name: args[:name])
    puts "Generated API Key: #{api_key.key}"
    puts "Name: #{api_key.name}"
  end
end 