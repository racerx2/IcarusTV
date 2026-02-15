// Copyright Epic Games, Inc. All Rights Reserved.
/*===========================================================================
	Generated code exported from UnrealHeaderTool.
	DO NOT modify this manually! Edit the corresponding .h files instead!
===========================================================================*/

#include "UObject/GeneratedCppIncludes.h"
#include "IcarusTVMod/Public/PowerToggleableStub.h"
#ifdef _MSC_VER
#pragma warning (push)
#pragma warning (disable : 4883)
#endif
PRAGMA_DISABLE_DEPRECATION_WARNINGS
void EmptyLinkFunctionForGeneratedCodePowerToggleableStub() {}
// Cross Module References
	ICARUSTVMOD_API UClass* Z_Construct_UClass_APowerToggleableStub_NoRegister();
	ICARUSTVMOD_API UClass* Z_Construct_UClass_APowerToggleableStub();
	ENGINE_API UClass* Z_Construct_UClass_AActor();
	UPackage* Z_Construct_UPackage__Script_IcarusTVMod();
	ENGINE_API UClass* Z_Construct_UClass_AActor_NoRegister();
// End Cross Module References
	static FName NAME_APowerToggleableStub_Deployable_Interact = FName(TEXT("Deployable_Interact"));
	void APowerToggleableStub::Deployable_Interact(AActor* Interactor)
	{
		PowerToggleableStub_eventDeployable_Interact_Parms Parms;
		Parms.Interactor=Interactor;
		ProcessEvent(FindFunctionChecked(NAME_APowerToggleableStub_Deployable_Interact),&Parms);
	}
	static FName NAME_APowerToggleableStub_OnDeviceStartRunning = FName(TEXT("OnDeviceStartRunning"));
	void APowerToggleableStub::OnDeviceStartRunning()
	{
		ProcessEvent(FindFunctionChecked(NAME_APowerToggleableStub_OnDeviceStartRunning),NULL);
	}
	static FName NAME_APowerToggleableStub_OnDeviceStopRunning = FName(TEXT("OnDeviceStopRunning"));
	void APowerToggleableStub::OnDeviceStopRunning()
	{
		ProcessEvent(FindFunctionChecked(NAME_APowerToggleableStub_OnDeviceStopRunning),NULL);
	}
	static FName NAME_APowerToggleableStub_OnDeviceTurnedOff = FName(TEXT("OnDeviceTurnedOff"));
	void APowerToggleableStub::OnDeviceTurnedOff()
	{
		ProcessEvent(FindFunctionChecked(NAME_APowerToggleableStub_OnDeviceTurnedOff),NULL);
	}
	static FName NAME_APowerToggleableStub_OnDeviceTurnedOn = FName(TEXT("OnDeviceTurnedOn"));
	void APowerToggleableStub::OnDeviceTurnedOn()
	{
		ProcessEvent(FindFunctionChecked(NAME_APowerToggleableStub_OnDeviceTurnedOn),NULL);
	}
	void APowerToggleableStub::StaticRegisterNativesAPowerToggleableStub()
	{
	}
	struct Z_Construct_UFunction_APowerToggleableStub_Deployable_Interact_Statics
	{
		static const UE4CodeGen_Private::FObjectPropertyParams NewProp_Interactor;
		static const UE4CodeGen_Private::FPropertyParamsBase* const PropPointers[];
#if WITH_METADATA
		static const UE4CodeGen_Private::FMetaDataPairParam Function_MetaDataParams[];
#endif
		static const UE4CodeGen_Private::FFunctionParams FuncParams;
	};
	const UE4CodeGen_Private::FObjectPropertyParams Z_Construct_UFunction_APowerToggleableStub_Deployable_Interact_Statics::NewProp_Interactor = { "Interactor", nullptr, (EPropertyFlags)0x0010000000000080, UE4CodeGen_Private::EPropertyGenFlags::Object, RF_Public|RF_Transient|RF_MarkAsNative, 1, STRUCT_OFFSET(PowerToggleableStub_eventDeployable_Interact_Parms, Interactor), Z_Construct_UClass_AActor_NoRegister, METADATA_PARAMS(nullptr, 0) };
	const UE4CodeGen_Private::FPropertyParamsBase* const Z_Construct_UFunction_APowerToggleableStub_Deployable_Interact_Statics::PropPointers[] = {
		(const UE4CodeGen_Private::FPropertyParamsBase*)&Z_Construct_UFunction_APowerToggleableStub_Deployable_Interact_Statics::NewProp_Interactor,
	};
#if WITH_METADATA
	const UE4CodeGen_Private::FMetaDataPairParam Z_Construct_UFunction_APowerToggleableStub_Deployable_Interact_Statics::Function_MetaDataParams[] = {
		{ "ModuleRelativePath", "Public/PowerToggleableStub.h" },
	};
#endif
	const UE4CodeGen_Private::FFunctionParams Z_Construct_UFunction_APowerToggleableStub_Deployable_Interact_Statics::FuncParams = { (UObject*(*)())Z_Construct_UClass_APowerToggleableStub, nullptr, "Deployable_Interact", nullptr, nullptr, sizeof(PowerToggleableStub_eventDeployable_Interact_Parms), Z_Construct_UFunction_APowerToggleableStub_Deployable_Interact_Statics::PropPointers, UE_ARRAY_COUNT(Z_Construct_UFunction_APowerToggleableStub_Deployable_Interact_Statics::PropPointers), RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x0C020800, 0, 0, METADATA_PARAMS(Z_Construct_UFunction_APowerToggleableStub_Deployable_Interact_Statics::Function_MetaDataParams, UE_ARRAY_COUNT(Z_Construct_UFunction_APowerToggleableStub_Deployable_Interact_Statics::Function_MetaDataParams)) };
	UFunction* Z_Construct_UFunction_APowerToggleableStub_Deployable_Interact()
	{
		static UFunction* ReturnFunction = nullptr;
		if (!ReturnFunction)
		{
			UE4CodeGen_Private::ConstructUFunction(ReturnFunction, Z_Construct_UFunction_APowerToggleableStub_Deployable_Interact_Statics::FuncParams);
		}
		return ReturnFunction;
	}
	struct Z_Construct_UFunction_APowerToggleableStub_OnDeviceStartRunning_Statics
	{
#if WITH_METADATA
		static const UE4CodeGen_Private::FMetaDataPairParam Function_MetaDataParams[];
#endif
		static const UE4CodeGen_Private::FFunctionParams FuncParams;
	};
#if WITH_METADATA
	const UE4CodeGen_Private::FMetaDataPairParam Z_Construct_UFunction_APowerToggleableStub_OnDeviceStartRunning_Statics::Function_MetaDataParams[] = {
		{ "ModuleRelativePath", "Public/PowerToggleableStub.h" },
	};
#endif
	const UE4CodeGen_Private::FFunctionParams Z_Construct_UFunction_APowerToggleableStub_OnDeviceStartRunning_Statics::FuncParams = { (UObject*(*)())Z_Construct_UClass_APowerToggleableStub, nullptr, "OnDeviceStartRunning", nullptr, nullptr, 0, nullptr, 0, RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x0C020800, 0, 0, METADATA_PARAMS(Z_Construct_UFunction_APowerToggleableStub_OnDeviceStartRunning_Statics::Function_MetaDataParams, UE_ARRAY_COUNT(Z_Construct_UFunction_APowerToggleableStub_OnDeviceStartRunning_Statics::Function_MetaDataParams)) };
	UFunction* Z_Construct_UFunction_APowerToggleableStub_OnDeviceStartRunning()
	{
		static UFunction* ReturnFunction = nullptr;
		if (!ReturnFunction)
		{
			UE4CodeGen_Private::ConstructUFunction(ReturnFunction, Z_Construct_UFunction_APowerToggleableStub_OnDeviceStartRunning_Statics::FuncParams);
		}
		return ReturnFunction;
	}
	struct Z_Construct_UFunction_APowerToggleableStub_OnDeviceStopRunning_Statics
	{
#if WITH_METADATA
		static const UE4CodeGen_Private::FMetaDataPairParam Function_MetaDataParams[];
#endif
		static const UE4CodeGen_Private::FFunctionParams FuncParams;
	};
#if WITH_METADATA
	const UE4CodeGen_Private::FMetaDataPairParam Z_Construct_UFunction_APowerToggleableStub_OnDeviceStopRunning_Statics::Function_MetaDataParams[] = {
		{ "ModuleRelativePath", "Public/PowerToggleableStub.h" },
	};
#endif
	const UE4CodeGen_Private::FFunctionParams Z_Construct_UFunction_APowerToggleableStub_OnDeviceStopRunning_Statics::FuncParams = { (UObject*(*)())Z_Construct_UClass_APowerToggleableStub, nullptr, "OnDeviceStopRunning", nullptr, nullptr, 0, nullptr, 0, RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x0C020800, 0, 0, METADATA_PARAMS(Z_Construct_UFunction_APowerToggleableStub_OnDeviceStopRunning_Statics::Function_MetaDataParams, UE_ARRAY_COUNT(Z_Construct_UFunction_APowerToggleableStub_OnDeviceStopRunning_Statics::Function_MetaDataParams)) };
	UFunction* Z_Construct_UFunction_APowerToggleableStub_OnDeviceStopRunning()
	{
		static UFunction* ReturnFunction = nullptr;
		if (!ReturnFunction)
		{
			UE4CodeGen_Private::ConstructUFunction(ReturnFunction, Z_Construct_UFunction_APowerToggleableStub_OnDeviceStopRunning_Statics::FuncParams);
		}
		return ReturnFunction;
	}
	struct Z_Construct_UFunction_APowerToggleableStub_OnDeviceTurnedOff_Statics
	{
#if WITH_METADATA
		static const UE4CodeGen_Private::FMetaDataPairParam Function_MetaDataParams[];
#endif
		static const UE4CodeGen_Private::FFunctionParams FuncParams;
	};
#if WITH_METADATA
	const UE4CodeGen_Private::FMetaDataPairParam Z_Construct_UFunction_APowerToggleableStub_OnDeviceTurnedOff_Statics::Function_MetaDataParams[] = {
		{ "ModuleRelativePath", "Public/PowerToggleableStub.h" },
	};
#endif
	const UE4CodeGen_Private::FFunctionParams Z_Construct_UFunction_APowerToggleableStub_OnDeviceTurnedOff_Statics::FuncParams = { (UObject*(*)())Z_Construct_UClass_APowerToggleableStub, nullptr, "OnDeviceTurnedOff", nullptr, nullptr, 0, nullptr, 0, RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x0C020800, 0, 0, METADATA_PARAMS(Z_Construct_UFunction_APowerToggleableStub_OnDeviceTurnedOff_Statics::Function_MetaDataParams, UE_ARRAY_COUNT(Z_Construct_UFunction_APowerToggleableStub_OnDeviceTurnedOff_Statics::Function_MetaDataParams)) };
	UFunction* Z_Construct_UFunction_APowerToggleableStub_OnDeviceTurnedOff()
	{
		static UFunction* ReturnFunction = nullptr;
		if (!ReturnFunction)
		{
			UE4CodeGen_Private::ConstructUFunction(ReturnFunction, Z_Construct_UFunction_APowerToggleableStub_OnDeviceTurnedOff_Statics::FuncParams);
		}
		return ReturnFunction;
	}
	struct Z_Construct_UFunction_APowerToggleableStub_OnDeviceTurnedOn_Statics
	{
#if WITH_METADATA
		static const UE4CodeGen_Private::FMetaDataPairParam Function_MetaDataParams[];
#endif
		static const UE4CodeGen_Private::FFunctionParams FuncParams;
	};
#if WITH_METADATA
	const UE4CodeGen_Private::FMetaDataPairParam Z_Construct_UFunction_APowerToggleableStub_OnDeviceTurnedOn_Statics::Function_MetaDataParams[] = {
		{ "ModuleRelativePath", "Public/PowerToggleableStub.h" },
	};
#endif
	const UE4CodeGen_Private::FFunctionParams Z_Construct_UFunction_APowerToggleableStub_OnDeviceTurnedOn_Statics::FuncParams = { (UObject*(*)())Z_Construct_UClass_APowerToggleableStub, nullptr, "OnDeviceTurnedOn", nullptr, nullptr, 0, nullptr, 0, RF_Public|RF_Transient|RF_MarkAsNative, (EFunctionFlags)0x0C020800, 0, 0, METADATA_PARAMS(Z_Construct_UFunction_APowerToggleableStub_OnDeviceTurnedOn_Statics::Function_MetaDataParams, UE_ARRAY_COUNT(Z_Construct_UFunction_APowerToggleableStub_OnDeviceTurnedOn_Statics::Function_MetaDataParams)) };
	UFunction* Z_Construct_UFunction_APowerToggleableStub_OnDeviceTurnedOn()
	{
		static UFunction* ReturnFunction = nullptr;
		if (!ReturnFunction)
		{
			UE4CodeGen_Private::ConstructUFunction(ReturnFunction, Z_Construct_UFunction_APowerToggleableStub_OnDeviceTurnedOn_Statics::FuncParams);
		}
		return ReturnFunction;
	}
	UClass* Z_Construct_UClass_APowerToggleableStub_NoRegister()
	{
		return APowerToggleableStub::StaticClass();
	}
	struct Z_Construct_UClass_APowerToggleableStub_Statics
	{
		static UObject* (*const DependentSingletons[])();
		static const FClassFunctionLinkInfo FuncInfo[];
#if WITH_METADATA
		static const UE4CodeGen_Private::FMetaDataPairParam Class_MetaDataParams[];
#endif
		static const FCppClassTypeInfoStatic StaticCppClassTypeInfo;
		static const UE4CodeGen_Private::FClassParams ClassParams;
	};
	UObject* (*const Z_Construct_UClass_APowerToggleableStub_Statics::DependentSingletons[])() = {
		(UObject* (*)())Z_Construct_UClass_AActor,
		(UObject* (*)())Z_Construct_UPackage__Script_IcarusTVMod,
	};
	const FClassFunctionLinkInfo Z_Construct_UClass_APowerToggleableStub_Statics::FuncInfo[] = {
		{ &Z_Construct_UFunction_APowerToggleableStub_Deployable_Interact, "Deployable_Interact" }, // 1995922407
		{ &Z_Construct_UFunction_APowerToggleableStub_OnDeviceStartRunning, "OnDeviceStartRunning" }, // 881996541
		{ &Z_Construct_UFunction_APowerToggleableStub_OnDeviceStopRunning, "OnDeviceStopRunning" }, // 439901469
		{ &Z_Construct_UFunction_APowerToggleableStub_OnDeviceTurnedOff, "OnDeviceTurnedOff" }, // 4026819655
		{ &Z_Construct_UFunction_APowerToggleableStub_OnDeviceTurnedOn, "OnDeviceTurnedOn" }, // 1706295090
	};
#if WITH_METADATA
	const UE4CodeGen_Private::FMetaDataPairParam Z_Construct_UClass_APowerToggleableStub_Statics::Class_MetaDataParams[] = {
		{ "BlueprintType", "true" },
		{ "IncludePath", "PowerToggleableStub.h" },
		{ "IsBlueprintBase", "true" },
		{ "ModuleRelativePath", "Public/PowerToggleableStub.h" },
	};
#endif
	const FCppClassTypeInfoStatic Z_Construct_UClass_APowerToggleableStub_Statics::StaticCppClassTypeInfo = {
		TCppClassTypeTraits<APowerToggleableStub>::IsAbstract,
	};
	const UE4CodeGen_Private::FClassParams Z_Construct_UClass_APowerToggleableStub_Statics::ClassParams = {
		&APowerToggleableStub::StaticClass,
		"Engine",
		&StaticCppClassTypeInfo,
		DependentSingletons,
		FuncInfo,
		nullptr,
		nullptr,
		UE_ARRAY_COUNT(DependentSingletons),
		UE_ARRAY_COUNT(FuncInfo),
		0,
		0,
		0x008000A4u,
		METADATA_PARAMS(Z_Construct_UClass_APowerToggleableStub_Statics::Class_MetaDataParams, UE_ARRAY_COUNT(Z_Construct_UClass_APowerToggleableStub_Statics::Class_MetaDataParams))
	};
	UClass* Z_Construct_UClass_APowerToggleableStub()
	{
		static UClass* OuterClass = nullptr;
		if (!OuterClass)
		{
			UE4CodeGen_Private::ConstructUClass(OuterClass, Z_Construct_UClass_APowerToggleableStub_Statics::ClassParams);
		}
		return OuterClass;
	}
	IMPLEMENT_CLASS(APowerToggleableStub, 3806733636);
	template<> ICARUSTVMOD_API UClass* StaticClass<APowerToggleableStub>()
	{
		return APowerToggleableStub::StaticClass();
	}
	static FCompiledInDefer Z_CompiledInDefer_UClass_APowerToggleableStub(Z_Construct_UClass_APowerToggleableStub, &APowerToggleableStub::StaticClass, TEXT("/Script/IcarusTVMod"), TEXT("APowerToggleableStub"), false, nullptr, nullptr, nullptr);
	DEFINE_VTABLE_PTR_HELPER_CTOR(APowerToggleableStub);
PRAGMA_ENABLE_DEPRECATION_WARNINGS
#ifdef _MSC_VER
#pragma warning (pop)
#endif
